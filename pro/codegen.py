import struct

from .parse import Address, Symbol, Expression, Var, Array, Const, Func
from .ropchain import RopChain, RopChunk, Marker

class CodeGenError(Exception):
    pass

class CodeGen(object):
    def __init__(self, prog):
        self.prog = prog
        self.data = None
        self.code = None

    def gen_chain(self, reloc={}):
        self._code = self.gen_code(self.prog.statements)

        # no relocation for data
        if '_DATA' not in reloc and '_CODE' in reloc:
            # we append .data to .code by default, so we can calculate the
            # .data base by .code base
            reloc['_DATA'] = reloc['_CODE'] + self._code.size

        self._data = self.gen_data(self.prog.env)

        self.code = self.flatten(self._code, reloc)
        self.data = self.flatten(self._data, reloc)

        return self.code + self.data

    def gen_data(self, env):
        # TODO eliminate unused data
        if env.size % 8 != 0:
            raise CodeGenError('.data not aligned')
        data = [0] * (env.size / 8)
        for v in env.vars.itervalues():
            val = None
            if isinstance(v, Var):
                val = v.value
                if val is not None:
                    val = [self._concretize(val, None)]
            elif isinstance(v, Array):
                val = v.data
                if isinstance(val, (str, unicode)):
                    raw = str(val).ljust(v.size, '\x00')
                else:
                    raw = '\x00' * v.size
                val = struct.unpack('<' + 'Q' * (len(raw) / 8), raw)
            if val is not None:
                if v.size % 8 != 0:
                    raise CodeGenError('%r is not aligned' % v)
                offset = v.addr.offset
                if not (offset >= 0 and (offset + v.size) <= env.size):
                    raise CodeGenError('inconsitent variable size')
                for i in xrange(v.size / 8):
                    data[offset / 8 + i] = val[i]
        return data

    def gen_code(self, statements):
        chain = RopChain()
        for stmt in statements:
            c = self.gen_call(stmt)
            c.define = set()
            c.reserve = set()
            chain.extends(c)
        return chain.final()

    def concretize(self, chain, reloc=None):
        # adjust function call which requires stack alignment
        for i in xrange(len(chain)):
            if isinstance(chain[i], Func) and chain[i].align:
                if not '_CODE' in reloc:
                    raise CodeGenError('base of .code is required for stack aligment')
                if (reloc['_CODE'] + i * 8) % 0x10 == 0:
                    # no need for alignment
                    continue
                nop = self.prog.env['nop']
                if chain[i + 1] != nop:
                    raise CodeGenError('no nop for stack alignment')
                # swap their order
                chain[i + 1] = chain[i]
                chain[i] = nop

        return map(lambda x:self._concretize(x, reloc), chain)

    def flatten(self, chain, reloc=None):
        return ''.join(map(lambda x: struct.pack('<Q', x & 0xFFFFFFFFFFFFFFFF), self.concretize(chain, reloc)))

    def gen_call(self, call):
        chunk = RopChunk()

        func = call.func

        if isinstance(func, Const) and func.name == 'inline':
            # `inline` is a virtual function, it glues all arguments
            r = RopChain(call.args)
            # FIXME we known nothing about the register usage in this RopChain
            return r

        # TODO support more flexible calling convention
        if isinstance(func, Func) and func.input is not None:
            # custom calling convention
            for k, arg in enumerate(call.args):
                reg = func.input[k]
                r = self.set_reg(reg, arg)
                r.reserve = {reg}
                chunk.append(r)
        else:
            # default calling convention
            for k, arg in enumerate(call.args):
                r = self.load_call_arg(k, arg)
                chunk.append(r)

        if isinstance(func, (Func, Const)):
            if isinstance(func, Func) and func.align:
                # we should have stack aligned when calling to this
                # function, usually the reason is the usage of floating
                # registers (e.g. printf). We add a nop gadget with the
                # Func, then reordering them when relocate the chain.
                nop = self.prog.env['nop']
                r = RopChain([func, nop])
            else:
                r = RopChain([func])
            r.reserve = {'all'} # all is a virtual register
            chunk.append(r)
        elif isinstance(func, Var):
            dst = Marker()
            r = RopChain([id(dst)])
            r.reserve = {'all'}
            chunk.append(r)

            r = self.ptrcpy(dst, func.addr)
            chunk.append(r)

        chain = chunk.compact()

        chain.extends(self.gen_call_epilog(len(call.args)))

        return chain

    def load_call_arg(self, k, arg):
        ''' set kth argument for current call statement '''
        raise CodeGenError('unimplemented method')

    def gen_call_epilog(self, argc):
        ''' clear args for a call statement '''
        raise CodeGenError('unimplemented method')

    def set_reg_imm(self, reg, imm):
        ''' load value of an immediate to a register '''
        raise CodeGenError('unimplemented method')

    def load_reg_mem(self, reg, addr):
        ''' load value from an address to a register '''
        raise CodeGenError('unimplemented method')

    def store_reg_mem(self, reg, addr):
        ''' store value of a register to an address '''
        raise CodeGenError('unimplemented method')

    def set_reg(self, reg, val):
        if isinstance(val, Var):
            return self.load_reg_mem(reg, val.addr)
        elif isinstance(val, Const) and val.name == 'undefined':
            # do not set undefined values
            return RopChain()
        else:
            return self.set_reg_imm(reg, val);

    def memcpy(self, dest, src, l):
        raise CodeGenError('unimplemented method')

    def ptrcpy(self, dest, src):
        ''' copy a pointer (8 bytes) '''
        raise CodeGenError('unimplemented method')

    def _concretize(self, var, reloc=None):
        if reloc is None:
            reloc = getattr(self, 'reloc', None)
        while isinstance(var, Expression):
            var = var.eval(reloc)
        return var

class CodeGenAmd64(CodeGen):
    def load_call_arg(self, k, arg):
        if k > 6:
            raise CodeGenError('only support 6 arguments')
        reg = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9'][k]
        r = self.set_reg(reg, arg)
        r.reserve = {reg}
        return r

    def gen_call_epilog(self, argc):
        return RopChain()

    def set_reg_imm(self, reg, imm):
        reg_setter = 'set_' + reg
        if reg_setter not in self.prog.env:
            raise CodeGenError('gadget "%s" is required' % reg_setter)
        gadget = self.prog.env[reg_setter]
        r = RopChain([gadget, imm])
        if gadget.clobber is not None:
            r.define |= set(gadget.clobber)
        if gadget.output is not None:
            r.define |= set(gadget.clobber)
        return r

    def load_reg_mem(self, reg, addr):
        # XXX load registers by RAX
        if reg == 'rax':
            load_rax = self.prog.env['load_rax'] # mov rax, qword ptr [rax]
            r = self.set_reg_imm(reg, addr)
            r.append(load_rax)
            r.define = {'rax'}
            return r
        else:
            dst = Marker()
            r = self.ptrcpy(dst, addr).extends(self.set_reg_imm(reg, id(dst)))
            return r

    def store_reg_mem(self, reg, addr):
        # XXX store registers in RAX
        if reg == 'rax':
            store_rdi_rax = self.prog.env['store_rdi_rax'] # mov qword ptr [rdi], rax
            r = self.set_reg_imm('rdi', addr)
            r.append(store_rdi_rax)
            r.define |= {'rdi'} # rdi is overwritten
            return r
        raise NotImplementedError('store_reg_mem %s' % reg)

    def ptrcpy(self, dest, src):
        r = self.load_reg_mem('rax', src).extends(self.store_reg_mem('rax', dest))
        return r
