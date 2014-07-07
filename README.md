Boa
-----

Tcp proxy that is pausable.

To run: 

```
:~#python boa.py [input port] [output port] [pause seconds]
```
Then to pause send a USR1 signal to the proccess:

```
:~#pkill -USR1 python
```
or

```
:~#ps -Al
to get the pid

:~#kill -USR1 [pid]
```