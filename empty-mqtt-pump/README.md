

Given an shell session on an empty Ubuntu 22.04 (or later) server, ensure it is uptodate, and then
run the script that installs what is needed:

```
 sudo apt update

 sudo apt upgrade

 git clone https://github.com/MetPX/sr3-examples/

```

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

(the rabbitmq one omitted... it's long, takes a few minutes.)
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

```


