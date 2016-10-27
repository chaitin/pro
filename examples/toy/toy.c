#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define SIZE 0x4000

int main()
{
	char *ropbuf = malloc(SIZE);
	read(0, ropbuf, SIZE);
	asm volatile ("mov %0, %%rsp\nret\n"::"m"(ropbuf));
}
