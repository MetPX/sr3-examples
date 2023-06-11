

Given an empty Ubuntu 22.04 (or later) run  the script here:

 sudo apt update

 sudo apt upgrade

 git clone https://github.com/MetPX/sr3-examples/

 ```bash

vmhost% cd sr3-examples/empty-mqtt-pump

vmhost% ./rabbitmq_pump_setup.sh
vmhost% ./add_mosquitto.sh

vmhost% sudo systemctl stop rabbitmq-server
vmhost% sudo systemctl disable rabbitmq-server

```

to:
  * install metpx-sr3c
  * install metpx-sr3
  * install and configure a rabbitmq message broker (then disable it.)
  * install and configure a mosquitto (MQTT) message broker.
  * have five basic mosquitto broker users configured:

    * bunnymaster - admin of the rabbitmq broker
    * tfeed - for flows set up by pump administratos.
    * tsource - an account to publish files with
    * tsub - an account to download files with.
    * and anonymous (an account to download using a public password.)

To this empty data pump can be added a lot of other layers of functionality.

sample run:

```bash

ubuntu@flow:~/sr3-examples/empty-mqtt-pump$ ./add_mosquitto.sh
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following additional packages will be installed:
  libcjson1 libdlt2 libev4 libmosquitto1 libwebsockets16
The following NEW packages will be installed:
  libcjson1 libdlt2 libev4 libmosquitto1 libwebsockets16 mosquitto mosquitto-clients
0 upgraded, 7 newly installed, 0 to remove and 0 not upgraded.
Need to get 648 kB of archives.
After this operation, 1967 kB of additional disk space will be used.
Get:1 http://archive.ubuntu.com/ubuntu jammy/universe amd64 libcjson1 amd64 1.7.15-1 [15.5 kB]
Get:2 http://archive.ubuntu.com/ubuntu jammy/universe amd64 libdlt2 amd64 2.18.6-2 [52.5 kB]
Get:3 http://archive.ubuntu.com/ubuntu jammy/universe amd64 libmosquitto1 amd64 2.0.11-1ubuntu1 [51.6 kB]
Get:4 http://archive.ubuntu.com/ubuntu jammy/universe amd64 libev4 amd64 1:4.33-1 [29.4 kB]
Get:5 http://archive.ubuntu.com/ubuntu jammy/universe amd64 libwebsockets16 amd64 4.0.20-2ubuntu1 [188 kB]
Get:6 http://archive.ubuntu.com/ubuntu jammy/universe amd64 mosquitto amd64 2.0.11-1ubuntu1 [239 kB]
Get:7 http://archive.ubuntu.com/ubuntu jammy/universe amd64 mosquitto-clients amd64 2.0.11-1ubuntu1 [72.6 kB]
Fetched 648 kB in 1s (792 kB/s)
Selecting previously unselected package libcjson1:amd64.
(Reading database ... 75025 files and directories currently installed.)
Preparing to unpack .../0-libcjson1_1.7.15-1_amd64.deb ...
Unpacking libcjson1:amd64 (1.7.15-1) ...
Selecting previously unselected package libdlt2:amd64.
Preparing to unpack .../1-libdlt2_2.18.6-2_amd64.deb ...
Unpacking libdlt2:amd64 (2.18.6-2) ...
Selecting previously unselected package libmosquitto1:amd64.
Preparing to unpack .../2-libmosquitto1_2.0.11-1ubuntu1_amd64.deb ...
Unpacking libmosquitto1:amd64 (2.0.11-1ubuntu1) ...
Selecting previously unselected package libev4:amd64.
Preparing to unpack .../3-libev4_1%3a4.33-1_amd64.deb ...
Unpacking libev4:amd64 (1:4.33-1) ...
Selecting previously unselected package libwebsockets16:amd64.
Preparing to unpack .../4-libwebsockets16_4.0.20-2ubuntu1_amd64.deb ...
Unpacking libwebsockets16:amd64 (4.0.20-2ubuntu1) ...
Selecting previously unselected package mosquitto.
Preparing to unpack .../5-mosquitto_2.0.11-1ubuntu1_amd64.deb ...
Unpacking mosquitto (2.0.11-1ubuntu1) ...
Selecting previously unselected package mosquitto-clients.
Preparing to unpack .../6-mosquitto-clients_2.0.11-1ubuntu1_amd64.deb ...
Unpacking mosquitto-clients (2.0.11-1ubuntu1) ...
Setting up libmosquitto1:amd64 (2.0.11-1ubuntu1) ...
Setting up libev4:amd64 (1:4.33-1) ...
Setting up libcjson1:amd64 (1.7.15-1) ...
Setting up mosquitto-clients (2.0.11-1ubuntu1) ...
Setting up libdlt2:amd64 (2.18.6-2) ...
Setting up libwebsockets16:amd64 (4.0.20-2ubuntu1) ...
Setting up mosquitto (2.0.11-1ubuntu1) ...
Created symlink /etc/systemd/system/multi-user.target.wants/mosquitto.service → /lib/systemd/system/mosquitto.service.
Processing triggers for man-db (2.10.2-1) ...
Processing triggers for libc-bin (2.35-0ubuntu3.1) ...
Scanning processes...
Scanning linux images...

Running kernel seems to be up-to-date.

No services need to be restarted.

No containers need to be restarted.

No user sessions are running outdated binaries.

No VM guests are running outdated hypervisor (qemu) binaries on this host.

ubuntu@flow:~/sr3-examples/empty-mqtt-pump$ sudo systemctl stop rabbitmq-server
ubuntu@flow:~/sr3-examples/empty-mqtt-pump$  sudo systemctl disable rabbitmq-server
Synchronizing state of rabbitmq-server.service with SysV service script with /lib/systemd/systemd-sysv-install.
Executing: /lib/systemd/systemd-sysv-install disable rabbitmq-server
Removed /etc/systemd/system/multi-user.target.wants/rabbitmq-server.service.
ubuntu@flow:~/sr3-examples/empty-mqtt-pump$ pwd
/home/ubuntu/sr3-examples/empty-mqtt-pump
ubuntu@flow:~/sr3-examples/empty-mqtt-pump$ ls config
sr3
ubuntu@flow:~/sr3-examples/empty-mqtt-pump$ mkdir ~/.config/sr3/sarra ~/.config/sr3/subscribe
ubuntu@flow:~/sr3-examples/empty-mqtt-pump$  cp config/sr3/subscribe/roundtrip.conf ~/.config/sr3/subscribe
ubuntu@flow:~/sr3-examples/empty-mqtt-pump$  cp config/sr3/sarra/hpfx_amis_to_local_mqtt.conf ~/.config/sr3/sarra
ubuntu@flow:~/sr3-examples/empty-mqtt-pump$  sr3 declare subscribe/roundtrip sarra/hpfx_amis_to_local_mqtt
2023-06-10 21:46:41,953 6152 [INFO] sarracenia.config finalize overriding batch for consistency with messageCountMax: 3
declare: 2023-06-10 21:46:41,954 6152 [INFO] root declare looking at sarra/hpfx_amis_to_local_mqtt
2023-06-10 21:46:41,955 6152 [WARNING] sarracenia.moth.mqtt __init__ note: mqtt support is newish, not very well tested
2023-06-10 21:46:41,955 6152 [INFO] root declare looking at subscribe/roundtrip
2023-06-10 21:46:41,955 6152 [INFO] root declare looking at sarra/hpfx_amis_to_local_mqtt
2023-06-10 21:46:42,163 6152 [INFO] sarracenia.moth.amqp __getSetup queue declared q_anonymous_sarra.hpfx_amis_to_local_mqtt.65224779.33910803 (as: amqps://anonymous@hpfx.collab.science.gc.ca/)
2023-06-10 21:46:42,163 6152 [INFO] sarracenia.moth.amqp __getSetup binding q_anonymous_sarra.hpfx_amis_to_local_mqtt.65224779.33910803 with v02.post.*.WXO-DD.bulletins.alphanumeric.# to xpublic (as: amqps://anonymous@hpfx.collab.science.gc.ca/)
2023-06-10 21:46:42,193 6152 [INFO] root declare looking at subscribe/roundtrip
2023-06-10 21:46:42,193 6152 [INFO] sarracenia.moth.mqtt __getSetup is no around? 0
2023-06-10 21:46:42,194 6152 [INFO] sarracenia.moth.mqtt __getSetup declare session for instances q_tsource_subscribe.roundtrip.53548250.26240450_i01
2023-06-10 21:46:42,194 6152 [DEBUG] sarracenia.moth.mqtt __sub_on_connect client=<paho.mqtt.client.Client object at 0x7fc67961a860> rc=Connection Accepted., flags={'session present': 0}
2023-06-10 21:46:42,195 6152 [DEBUG] sarracenia.moth.mqtt __sub_on_connect no existing session, no recovery of inflight messages from previous connection
2023-06-10 21:46:42,195 6152 [INFO] sarracenia.moth.mqtt __sub_on_connect tuple: xs_tsource ['v03'] ['#']
2023-06-10 21:46:42,195 6152 [INFO] sarracenia.moth.mqtt __sub_on_connect asked to subscribe to: $share/q_tsource_subscribe.roundtrip.53548250.26240450/xs_tsource/v03/#, mid=1 qos=1 result: No error.
2023-06-10 21:46:42,195 6152 [INFO] sarracenia.moth.mqtt __sub_on_subscribe client: b'q_tsource_subscribe.roundtrip.53548250.26240450_i01' subscribe completed mid=1 granted_qos=['Granted QoS 1']
2023-06-10 21:46:42,195 6152 [DEBUG] sarracenia.moth.mqtt __sub_on_disconnect Connection Accepted.
2023-06-10 21:46:42,196 6152 [INFO] sarracenia.moth.mqtt __getSetup instance declaration for q_tsource_subscribe.roundtrip.53548250.26240450_i01 done
2023-06-10 21:46:42,196 6152 [WARNING] sarracenia.moth.mqtt __init__ note: mqtt support is newish, not very well tested
2023-06-10 21:46:42,196 6152 [INFO] sarracenia.moth.mqtt close closing

ubuntu@flow:~/sr3-examples/empty-mqtt-pump$ sr3 status
2023-06-10 21:47:09,910 6154 [INFO] sarracenia.config finalize overriding batch for consistency with messageCountMax: 3
status:
Component/Config                         Processes   Connection        Lag                Rates
                                         State   Run Retry  msg data   LagMax  LagAvg  %rej     pubsub   messages     RxData     TxData
                                         -----   --- -----  --- ----   ------  ------  ----   --------       ----     ------     ------
sarra/hpfx_amis_to_local_mqtt            stop    0/0          -          -         -     -          -        -
subscribe/roundtrip                      stop    0/0          -          -         -     -          -        -
      Total Running Configs:   0 ( Processes: 0 missing: 0 stray: 0 )
                     Memory: uss:0 Bytes rss:0 Bytes vms:0 Bytes
                   CPU Time: User:0.00s System:0.00s
	   Pub/Sub Received: 0 msgs/s (0 Bytes/s), Sent:  0 msgs/s (0 Bytes/s)
	      Data Received: 0 Files/s (0 Bytes/s), Sent: 0 Files/s (0 Bytes/s)
ubuntu@flow:~/sr3-examples/empty-mqtt-pump$ sr3 start
2023-06-10 21:47:16,151 6155 [INFO] sarracenia.config finalize overriding batch for consistency with messageCountMax: 3
starting:.( 6 ) Done

ubuntu@flow:~/sr3-examples/empty-mqtt-pump$ cd ~/.cache/sr3/log
ubuntu@flow:~/.cache/sr3/log$ ls
sarra_hpfx_amis_to_local_mqtt_01.log  sarra_hpfx_amis_to_local_mqtt_03.log  sarra_hpfx_amis_to_local_mqtt_05.log
sarra_hpfx_amis_to_local_mqtt_02.log  sarra_hpfx_amis_to_local_mqtt_04.log  subscribe_roundtrip_01.log
ubuntu@flow:~/.cache/sr3/log$ more subscribe_roundtrip_01.log
2023-06-10 21:47:16,877 [INFO] sarracenia.flow loadCallbacks flowCallback plugins to load: ['sarracenia.flowcb.gather.message.Message', 'sarracenia.flowcb.re
try.Retry', 'sarracenia.flowcb.housekeeping.resources.Resources', 'log']
2023-06-10 21:47:16,879 [INFO] sarracenia.moth.mqtt __getSetup is no around? 1
2023-06-10 21:47:16,880 [WARNING] sarracenia.moth.mqtt __getSetup paho library using auto_ack. may lose data every crash or restart.
2023-06-10 21:47:16,883 [WARNING] sarracenia.moth.mqtt __init__ note: mqtt support is newish, not very well tested
2023-06-10 21:47:16,893 [DEBUG] sarracenia.moth.mqtt _easy_log Sending CONNECT (u1, p1, wr0, wq0, wf0, c0, k60) client_id=b'q_tsource_subscribe.roundtrip.535
48250.26240450_i01' properties=[SessionExpiryInterval : 600]
2023-06-10 21:47:16,893 [DEBUG] sarracenia.moth.mqtt _easy_log Received CONNACK (1, Success) properties=[ReceiveMaximum : 1000, TopicAliasMaximum : 10]
2023-06-10 21:47:16,893 [DEBUG] sarracenia.moth.mqtt __sub_on_connect client=<paho.mqtt.client.Client object at 0x7eff9e027c10> rc=Connection Accepted., flag
s={'session present': 1}
2023-06-10 21:47:16,893 [INFO] sarracenia.moth.mqtt __sub_on_connect tuple: xs_tsource ['v03'] ['#']
2023-06-10 21:47:16,893 [DEBUG] sarracenia.moth.mqtt _easy_log Sending SUBSCRIBE (d0, m1) [(b'$share/q_tsource_subscribe.roundtrip.53548250.26240450/xs_tsour
ce/v03/#', {QoS=1, noLocal=False, retainAsPublished=False, retainHandling=0})]
2023-06-10 21:47:16,894 [INFO] sarracenia.moth.mqtt __sub_on_connect asked to subscribe to: $share/q_tsource_subscribe.roundtrip.53548250.26240450/xs_tsource
/v03/#, mid=1 qos=1 result: No error.
2023-06-10 21:47:16,894 [DEBUG] sarracenia.moth.mqtt _easy_log Received SUBACK
2023-06-10 21:47:16,894 [INFO] sarracenia.moth.mqtt __sub_on_subscribe client: b'q_tsource_subscribe.roundtrip.53548250.26240450_i01' subscribe completed mid
=1 granted_qos=['Granted QoS 1']
2023-06-10 21:47:16,901 [INFO] sarracenia.flowcb.log __init__ subscribe initialized with: {'after_accept', 'after_work', 'on_housekeeping', 'post', 'after_po
st'}
2023-06-10 21:47:16,902 [ERROR] sarracenia.config check_undeclared_options undeclared option: topic
2023-06-10 21:47:16,902 [INFO] sarracenia.flow run callbacks loaded: ['sarracenia.flowcb.gather.message.Message', 'sarracenia.flowcb.retry.Retry', 'sarraceni
a.flowcb.housekeeping.resources.Resources', 'log']
2023-06-10 21:47:16,902 [INFO] sarracenia.flow run pid: 6161 subscribe/roundtrip instance: 1
2023-06-10 21:47:17,002 [INFO] sarracenia.flow run now active on vip None
ubuntu@flow:~/.cache/sr3/log$ more subscribe_roundtrip_01.log
2023-06-10 21:47:16,877 [INFO] sarracenia.flow loadCallbacks flowCallback plugins to load: ['sarracenia.flowcb.gather.message.Message', 'sarracenia.flowcb.re
try.Retry', 'sarracenia.flowcb.housekeeping.resources.Resources', 'log']
2023-06-10 21:47:16,879 [INFO] sarracenia.moth.mqtt __getSetup is no around? 1
2023-06-10 21:47:16,880 [WARNING] sarracenia.moth.mqtt __getSetup paho library using auto_ack. may lose data every crash or restart.
2023-06-10 21:47:16,883 [WARNING] sarracenia.moth.mqtt __init__ note: mqtt support is newish, not very well tested
2023-06-10 21:47:16,893 [DEBUG] sarracenia.moth.mqtt _easy_log Sending CONNECT (u1, p1, wr0, wq0, wf0, c0, k60) client_id=b'q_tsource_subscribe.roundtrip.535
48250.26240450_i01' properties=[SessionExpiryInterval : 600]
2023-06-10 21:47:16,893 [DEBUG] sarracenia.moth.mqtt _easy_log Received CONNACK (1, Success) properties=[ReceiveMaximum : 1000, TopicAliasMaximum : 10]
2023-06-10 21:47:16,893 [DEBUG] sarracenia.moth.mqtt __sub_on_connect client=<paho.mqtt.client.Client object at 0x7eff9e027c10> rc=Connection Accepted., flag
s={'session present': 1}
2023-06-10 21:47:16,893 [INFO] sarracenia.moth.mqtt __sub_on_connect tuple: xs_tsource ['v03'] ['#']
2023-06-10 21:47:16,893 [DEBUG] sarracenia.moth.mqtt _easy_log Sending SUBSCRIBE (d0, m1) [(b'$share/q_tsource_subscribe.roundtrip.53548250.26240450/xs_tsour
ce/v03/#', {QoS=1, noLocal=False, retainAsPublished=False, retainHandling=0})]
2023-06-10 21:47:16,894 [INFO] sarracenia.moth.mqtt __sub_on_connect asked to subscribe to: $share/q_tsource_subscribe.roundtrip.53548250.26240450/xs_tsource
/v03/#, mid=1 qos=1 result: No error.
2023-06-10 21:47:16,894 [DEBUG] sarracenia.moth.mqtt _easy_log Received SUBACK
2023-06-10 21:47:16,894 [INFO] sarracenia.moth.mqtt __sub_on_subscribe client: b'q_tsource_subscribe.roundtrip.53548250.26240450_i01' subscribe completed mid
=1 granted_qos=['Granted QoS 1']
2023-06-10 21:47:16,901 [INFO] sarracenia.flowcb.log __init__ subscribe initialized with: {'after_accept', 'after_work', 'on_housekeeping', 'post', 'after_po
st'}
2023-06-10 21:47:16,902 [ERROR] sarracenia.config check_undeclared_options undeclared option: topic
2023-06-10 21:47:16,902 [INFO] sarracenia.flow run callbacks loaded: ['sarracenia.flowcb.gather.message.Message', 'sarracenia.flowcb.retry.Retry', 'sarraceni
a.flowcb.housekeeping.resources.Resources', 'log']
2023-06-10 21:47:16,902 [INFO] sarracenia.flow run pid: 6161 subscribe/roundtrip instance: 1
2023-06-10 21:47:17,002 [INFO] sarracenia.flow run now active on vip None
ubuntu@flow:~/.cache/sr3/log$ ls
sarra_hpfx_amis_to_local_mqtt_01.log  sarra_hpfx_amis_to_local_mqtt_03.log  sarra_hpfx_amis_to_local_mqtt_05.log
sarra_hpfx_amis_to_local_mqtt_02.log  sarra_hpfx_amis_to_local_mqtt_04.log  subscribe_roundtrip_01.log
ubuntu@flow:~/.cache/sr3/log$ more sarra_hpfx_amis_to_local_mqtt_01.log
2023-06-10 21:47:16,840 [INFO] 6156 sarracenia.config finalize overriding batch for consistency with messageCountMax: 3
2023-06-10 21:47:16,851 [INFO] sarracenia.config finalize overriding batch for consistency with messageCountMax: 3
Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/sarracenia/instance.py", line 242, in <module>
    i.start()
  File "/usr/lib/python3/dist-packages/sarracenia/instance.py", line 231, in start
    self.running_instance = Flow.factory(cfg)
  File "/usr/lib/python3/dist-packages/sarracenia/flow/__init__.py", line 117, in factory
    return sc(cfg)
  File "/usr/lib/python3/dist-packages/sarracenia/flow/sarra.py", line 17, in __init__
    super().__init__(options)
  File "/usr/lib/python3/dist-packages/sarracenia/flow/__init__.py", line 181, in __init__
    ('sarracenia.flowcb.work.delete.Delete' not in self.plugins_late['load']):
AttributeError: 'Sarra' object has no attribute 'plugins_late'
ubuntu@flow:~/.cache/sr3/log$ pwd
/home/ubuntu/.cache/sr3/log
ubuntu@flow:~/.cache/sr3/log$ sr3 stop
2023-06-10 21:48:02,275 6168 [INFO] sarracenia.config finalize overriding batch for consistency with messageCountMax: 3
Stopping: sending SIGTERM . ( 1 ) Done
Waiting 1 sec. to check if 1 processes stopped (try: 0)
Waiting 2 sec. to check if 1 processes stopped (try: 1)
All stopped after try 1

ubuntu@flow:~/.cache/sr3/log$ cd
ubuntu@flow:~$ ls
sr3-examples
ubuntu@flow:~$ ls -al
total 40
drwxr-x--- 7 ubuntu ubuntu 4096 Jun 10 21:40 .
drwxr-xr-x 3 root   root   4096 Jun 10 21:35 ..
-rw-r--r-- 1 ubuntu ubuntu  220 Jan  6  2022 .bash_logout
-rw-r--r-- 1 ubuntu ubuntu 3771 Jan  6  2022 .bashrc
drwx------ 4 ubuntu ubuntu 4096 Jun 10 21:40 .cache
drwxrwxr-x 4 ubuntu ubuntu 4096 Jun 10 21:40 .config
drwxrwxr-x 4 ubuntu ubuntu 4096 Jun 10 21:40 .local
-rw-r--r-- 1 ubuntu ubuntu  807 Jan  6  2022 .profile
drwx------ 2 ubuntu ubuntu 4096 Jun 10 21:35 .ssh
-rw-r--r-- 1 ubuntu ubuntu    0 Jun 10 21:39 .sudo_as_admin_successful
drwxrwxr-x 7 ubuntu ubuntu 4096 Jun 10 21:39 sr3-examples
```


User Cases
==========

0. install dev branch or >= 3.0.41

```bash

ubuntu@flow:~$ git clone --branch sr3_issue615 https://github.com/MetPX/Sarracenia sr3
ubuntu@flow:~$ cd sr3
ubuntu@flow:~/sr3$ sudo apt remove metpx-sr3
ubuntu@flow:~/sr3$ pip install -e .

# get sr3 into the PATH...
ubuntu@flow:~/sr3$ exit
fractal% multipass shell flow

```

this time, with output:


```bash

ubuntu@flow:~$ git clone https://github.com/MetPX/Sarracenia sr3
Cloning into 'sr3'...
remote: Enumerating objects: 42406, done.
remote: Counting objects: 100% (2500/2500), done.
remote: Compressing objects: 100% (791/791), done.
remote: Total 42406 (delta 1736), reused 2323 (delta 1629), pack-reused 39906
Receiving objects: 100% (42406/42406), 23.94 MiB | 28.63 MiB/s, done.
Resolving deltas: 100% (31616/31616), done.
ubuntu@flow:~$ cd sr3
ubuntu@flow:~/sr3$ git checkout v3_issue615
error: pathspec 'v3_issue615' did not match any file(s) known to git
ubuntu@flow:~/sr3$ set -o vi
ubuntu@flow:~/sr3$ git checkout v03_issue615
Branch 'v03_issue615' set up to track remote branch 'v03_issue615' from 'origin'.
Switched to a new branch 'v03_issue615'
ubuntu@flow:~/sr3$ git pull
Already up to date.
ubuntu@flow:~/sr3$ sudo apt remove metpx-sr3
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following packages were automatically installed and are no longer required:
  ncftp python3-appdirs python3-humanfriendly python3-humanize python3-jsonpickle python3-nacl python3-paramiko python3-psutil python3-watchdog
Use 'sudo apt autoremove' to remove them.
The following packages will be REMOVED:
  metpx-sr3
0 upgraded, 0 newly installed, 1 to remove and 0 not upgraded.
After this operation, 1067 kB disk space will be freed.
Do you want to continue? [Y/n] y
(Reading database ... 75097 files and directories currently installed.)
Removing metpx-sr3 (3.00.40~ubuntu22.04.1) ...
ubuntu@flow:~/sr3$ pip install -e .
Defaulting to user installation because normal site-packages is not writeable
Obtaining file:///home/ubuntu/sr3
  Preparing metadata (setup.py) ... done
Requirement already satisfied: appdirs in /usr/lib/python3/dist-packages (from metpx-sr3==3.0.41) (1.4.4)
Requirement already satisfied: humanfriendly in /usr/lib/python3/dist-packages (from metpx-sr3==3.0.41) (10.0)
Requirement already satisfied: humanize in /usr/lib/python3/dist-packages (from metpx-sr3==3.0.41) (0.0.0)
Requirement already satisfied: jsonpickle in /usr/lib/python3/dist-packages (from metpx-sr3==3.0.41) (2.0.0+dfsg1)
Requirement already satisfied: paramiko in /usr/lib/python3/dist-packages (from metpx-sr3==3.0.41) (2.9.3)
Requirement already satisfied: psutil>=5.3.0 in /usr/lib/python3/dist-packages (from metpx-sr3==3.0.41) (5.9.0)
Requirement already satisfied: watchdog in /usr/lib/python3/dist-packages (from metpx-sr3==3.0.41) (2.1.6)
Installing collected packages: metpx-sr3
  Running setup.py develop for metpx-sr3
Successfully installed metpx-sr3

ubuntu@flow:~/sr3$ which sr3
ubuntu@flow:~/sr3$ exit
logout
fractal% multipass shell flow
Welcome to Ubuntu 22.04.2 LTS (GNU/Linux 5.15.0-73-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Sat Jun 10 21:49:27 EDT 2023

  System load:  0.05126953125     Processes:             91
  Usage of /:   9.0% of 28.89GB   Users logged in:       0
  Memory usage: 4%                IPv4 address for ens3: 10.110.41.32
  Swap usage:   0%


Expanded Security Maintenance for Applications is not enabled.

0 updates can be applied immediately.

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status


Last login: Sat Jun 10 21:36:48 2023 from 10.110.41.1
ubuntu@flow:~$ which sr3
/home/ubuntu/.local/bin/sr3
ubuntu@flow:~$

```

1. Publishing ECCC Datamart data to WMO/WIS data pump.


```bash

vmhost%  mkdir ~/.config/sr3/sarra ~/.config/sr3/subscribe
vmhost%  cp config/sr3/subscribe/roundtrip.conf ~/.config/sr3/subscribe
vmhost%  cp config/sr3/sarra/hpfx_amis_to_local_mqtt.conf ~/.config/sr3/sarra
vmhost%  sr3 declare subscribe/roundtrip sarra/hpfx_amis_to_local_mqtt


```

2. Run the test.

```bash

sr3 start

```

3. Review the results.

