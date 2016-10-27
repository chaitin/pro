{% if str(self) not in MODULES %}
# {{self if MODULES.add(str(self)) else self}}
{% if LIBC_VERSION == '2.23' %}

func nop <libc, 0x0002d822>;

func set_rax <libc, 0x0003a717, "rax:rax:">;
func set_rdi <libc, 0x00021192, "rdi:rdi:">;
func set_rsi <libc, 0x000203e6, "rsi:rsi:">;
func set_rdx <libc, 0x00001b92, "rdx:rdx:">;
func set_rcx <libc, 0x00050233, "rcx:rcx:">;
func set_r8 <libc, 0x00134946, "r8:r8:rax">; // pop r8 ; mov eax, 0x00000001 ; ret  ;
func set_r14 <libc, 0x000202e7, "r14:r14:">;
func set_rbx <libc, 0x0002a6ea, "rbx:rbx:">;
func set_rsp <libc, 0x0002e836, "rsp:rsp:">;

func store_rdx_rax <libc, 0x0002e19c, "rdx,rax::">;
func load_rax <libc, 0x00128208, "rax:rax:">;
func mov_r9_r14_call_rbx <libc, 0x0002185a, "r14,rbx:r9:r14,rbx">;

{% elif LIBC_VERSION == '2.21' %}

func nop <libc, 0x000237fd>;

func set_rax <libc, 0x0003a517, "rax:rax:">;
func set_rdi <libc, 0x0002464c, "rdi:rdi:">;
func set_rsi <libc, 0x000232f5, "rsi:rsi:">;
func set_rdx <libc, 0x00001b92, "rdx:rdx:">;
func set_rcx <libc, 0x0008d913, "rcx:rcx:">;
func set_r8 <libc, 0x00134766, "r8:r8:rax">; // pop r8 ; mov eax, 0x00000001 ; ret  ;
func set_r14 <libc, 0x000232f4, "r14:r14:">;
func set_r15 <libc, 0x000218b9, "r15:r15:">;
func set_rbx <libc, 0x0002ae85, "rbx:rbx:">;
func set_rsp <libc, 0x0002eaf0, "rsp:rsp:">;
func set_rbp <libc, 0x0002225e, "rbp:rbp:">;

func store_rdx_rax <libc, 0x0002e60c, "rdx,rax:rax:">;
func load_rax <libc, 0x00128aa8, "rax:rax:">;
func mov_r9_r15_call_rbx <libc, 0x000ac244, "r15,rbx:r9:r15,rbx">;

{% endif %}
{% endif %}
