main {
{% include "gadgets.pro" %}
{% include "glibc.pro" %}
printf("this is main!\n");
printf("this is main again!\n");
nop(); // stack alignment is fixed automatically
printf("this is main again and again!\n");
// put relay in the end of main
{% include "relay.pro" %}
printf("bye\n");
exit(0);
}
