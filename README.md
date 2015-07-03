# ansible

Examples:
[ec2-user@ip-172-31-24-63 ansible]$ python ansible.py
2015-07-03 07:45:07 : starting to provision 3 EC instance
2015-07-03 07:45:07 : waiting 10 minutes at most for the instance to be ready..
2015-07-03 07:45:08 : i-f6f91a3f 172.31.45.2 pending
2015-07-03 07:46:08 : i-f6f91a3f 172.31.45.2 running
2015-07-03 07:46:08 : i-15f81bdc 172.31.45.3 running
2015-07-03 07:46:08 : i-14f81bdd 172.31.45.1 running
2015-07-03 07:46:08 : sleeping 60 seconds before proceeding
2015-07-03 07:47:08 : checking ssh access for servers 172.31.45.2 i-f6f91a3f
2015-07-03 07:47:09 : checking ssh access for servers 172.31.45.3 i-15f81bdc
2015-07-03 07:47:09 : checking ssh access for servers 172.31.45.1 i-14f81bdd
2015-07-03 07:47:10 : copying the binary to the destination server:172.31.45.2 i-f6f91a3f
2015-07-03 07:47:18 : copying the binary to the destination server:172.31.45.3 i-15f81bdc
2015-07-03 07:47:24 : copying the binary to the destination server:172.31.45.1 i-14f81bdd
2015-07-03 07:47:29 : beginning install the package on the destination server:172.31.45.2 i-f6f91a3f
2015-07-03 07:47:34 : starting zookeeper service on the destination server:172.31.45.2 i-f6f91a3f
2015-07-03 07:47:35 : beginning install the package on the destination server:172.31.45.3 i-15f81bdc
2015-07-03 07:47:39 : starting zookeeper service on the destination server:172.31.45.3 i-15f81bdc
2015-07-03 07:47:40 : beginning install the package on the destination server:172.31.45.1 i-14f81bdd
2015-07-03 07:47:43 : starting zookeeper service on the destination server:172.31.45.1 i-14f81bdd
2015-07-03 07:47:44 : copying zk-smoketest to the last destination server:172.31.45.1 i-14f81bdd
2015-07-03 07:47:45 : using zk-smoketest to test the zookeeper service on the server:172.31.45.1 i-14f81bdd
Connecting to 172.31.45.1:2181
Connected in 1939 ms, handle is 0
Connecting to 172.31.45.3:2181
Connected in 415 ms, handle is 1
Connecting to 172.31.45.2:2181
Connected in 264 ms, handle is 2
Connecting to 172.31.45.1:2181
Connected in 10 ms, handle is 3
Connecting to 172.31.45.2:2181
Connected in 11 ms, handle is 0
Smoke test successful

