{% if str(self) not in MODULES %}
# {{self if MODULES.add(str(self)) else self}}
const AF_INET(2)
const SOCK_STREAM(1)
const IPPROTO_IP(0)

const PROT_NONE(0x0)
const PROT_READ(0x1)
const PROT_WRITE(0x2)
const PROT_EXEC(0x4)
const MAP_ANON(0x20) // linux
const MAP_SHARED(0x1)
const MAP_FIXED(0x10)
const MAP_PRIVATE(0x2)

{% if LIBC_VERSION == '2.23' %}

func mmap <libc, 0x0000000000100dc0>
func system <libc, 0x0000000000045380>
func socket <libc, 0x0000000000107ce0>
func connect <libc, 0x0000000000107860>
func dup2 <libc, 0x00000000000f70c0>
func printf <libc, 0x00000000000557b0, "rdi,rsi,rdx,rcx,r8,r9:::va,align">
func exit <libc, 0x000000000003a020>
func perror <libc, 0x000000000006a940>
func dprintf <libc, 0x0000000000055a10, "rdi,rsi,rdx,rcx,r8,r9:::va,align">
func read <libc, 0x00000000000f69a0>
func write <libc, 0x00000000000f6a00>

{% elif LIBC_VERSION == '2.21' %}

func mmap <libc, 0x00000000001016d0>
func system <libc, 0x000000000000443d0>
func socket <libc, 0x0000000000108060>
func connect <libc, 0x0000000000107be0>
func dup2 <libc, 0x00000000000f7b40>
func printf <libc, 0x0000000000054ba0, "rdi,rsi,rdx,rcx,r8,r9:::va,align">
func exit <libc, 0x0000000000039d70>
func perror <libc, 0x000000000006bd90>
func dprintf <libc, 0x0000000000054e00, "rdi,rsi,rdx,rcx,r8,r9:::va,align">
func read <libc, 0x00000000000f7420>
func write <libc, 0x00000000000f7480>

{% endif %}
{% endif %}
