
# Subscribe to Sarracenia Data pump, producing a WMO/WIS format message flow

Given one has installed a local mqtt broker, and sr3 then the following configurations are installed:

The sarra/hpfx_amis_to_local_mqtt configuration will:

* Subscribe (with AMQP) to a public Sarracenia data pump (hpfx.collab.science.gc.ca.)
  these messages use different checksums (producer choice.) WMO does not accept that different
  checksums are needed for different cases, so one must normalize it.  To do so:

* download the data into a temp. directory ( /tmp/hpfx_amis ) calculating a WMO compatible
  checksum as you do.

* after the file is downloaded, delete it.

* create messages in the WIS format ( geo-json with many other differences.)

  * formatting very different from sarracenia native.
  * relPath is not a concept, so file: path and name are not present in the messages.
  * there is a "topic" field that must be filled in (no known algorithm for filling that in correctly yet.)
  * data_id is a unique name for the product.
  * checksum must be sha512.  

* publish WIS format messages to mqtt broker on localhost that point back to hpfx.collab.scence.gc.ca for
  the retrieval URL.

The subscribe/roundtrip configuraration will:

* subscribe to the messages posted to the local mqtt broker by the sarra.
* download the files being advertised into /tmp/hpfx_roundtrip.
  
Note that the paths to files on the source (hpfx) and destination (localhost) are are very
different. This is a normal consequence of the differences in the notification format.


resources for WIS format notifications:

* https://github.com/wmo-im/pywis-pubsub
* https://github.com/ECCC-MSC/msc-wis2node
* https://wmo-im.github.io/wis2-notification-message/standard/wis2-notification-message-DRAFT.pdf


## Step 1: Install the formats, run sr3 declare:

```bash

vmhost%  mkdir ~/.config/sr3/sarra ~/.config/sr3/subscribe
vmhost%  cp config/sr3/subscribe/roundtrip.conf ~/.config/sr3/subscribe
vmhost%  cp config/sr3/sarra/hpfx_amis_to_local_mqtt.conf ~/.config/sr3/sarra
vmhost%  sr3 declare subscribe/roundtrip sarra/hpfx_amis_to_local_mqtt


```

sample run:

``bash

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

ubuntu@flow:~/sr3-examples/empty-mqtt-pump$ 
```


## Step 2: Install Correct dev branch or >= 3.0.41

The current release of sr3 does not work with WMO/WIS messages.

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

## Step 3:  Start up mosquitt_sub

To have a sr3 independent view of the messages, one can also start up mosquitto_sub.
Start a separate shell on the vm to see the raw messages:

```base

fractal% mosquitto_sub -v --pretty -h localhost -t '#' -F '%j %P'


```



## Step 4: Run the test.

```bash

sr3 start

```

Review the results:


  If you look in the log, there will be entries like:

```bash

ubuntu@flow:~/.cache/sr3/log$ more sarra_hpfx_amis_to_local_mqtt_01.log
2023-06-10 21:49:41,457 [INFO] 6367 sarracenia.config finalize overriding batch for consistency with messageCountMax: 3
2023-06-10 21:49:41,459 [INFO] sarracenia.config finalize overriding batch for consistency with messageCountMax: 3
2023-06-10 21:49:41,461 [INFO] sarracenia.flow loadCallbacks flowCallback plugins to load: ['sarracenia.flowcb.post.message.Message', 'sarracenia.flowcb.gather.message.Message', 'sarracenia.flow
cb.retry.Retry', 'sarracenia.flowcb.housekeeping.resources.Resources', 'accept.trim_legacy_fields', 'work.delete', 'log', 'sarracenia.flowcb.work.delete.Delete']
2023-06-10 21:49:41,462 [INFO] sarracenia.moth.mqtt __putSetup connecting to localhost, res=None
2023-06-10 21:49:41,465 [WARNING] sarracenia.moth.mqtt __init__ note: mqtt support is newish, not very well tested
2023-06-10 21:49:41,467 [INFO] sarracenia.moth.mqtt __pub_on_connect Connection Accepted.
2023-06-10 21:49:41,618 [INFO] sarracenia.moth.amqp __getSetup queue declared q_anonymous_sarra.hpfx_amis_to_local_mqtt.65224779.33910803 (as: amqps://anonymous@hpfx.collab.science.gc.ca/) 
2023-06-10 21:49:41,618 [INFO] sarracenia.moth.amqp __getSetup binding q_anonymous_sarra.hpfx_amis_to_local_mqtt.65224779.33910803 with v02.post.*.WXO-DD.bulletins.alphanumeric.# to xpublic (as:
 amqps://anonymous@hpfx.collab.science.gc.ca/)


```

the above show the sarra process binding to hpfx.collab.science.gc.ca with AMQP and subscribing to a selection of bulletins.
further down, there are message downloads shown in the log (extensive debugging is configured for this process.)

```
2023-06-10 21:49:41,658 [INFO] sarracenia.moth.amqp _msgRawToDict raw message start
2023-06-10 21:49:41,659 [INFO] sarracenia.moth.amqp _msgRawToDict body: type: <class 'str'> (139 bytes) 20230611014642.480 https://hpfx.collab.science.gc.ca /20230611/WXO-DD/bulletins/alphanumer
ic/20230611/SR/KWAL/01/SRME20_KWAL_110146___33624
2023-06-10 21:49:41,659 [INFO] sarracenia.moth.amqp _msgRawToDict headers: type: <class 'dict'> (9 elements) {'sundew_extension': 'cvt_nws_bulletins-sr:KWAL:SR:3:Direct:20230611014641', 'sum': '
d,77f6158abf3f27c276b42170a3c36060', 'from_cluster': 'DDSR.CMC', 'to_clusters': 'DDSR.CMC,DDI.CMC,CMC,SCIENCE,EDM', 'filename': 'msg_ddsr-WXO-DD3_793c4a7fec839fc97766e9b0781d40dc:cvt_nws_bulleti
ns-sr:KWAL:SR:3:Direct:20230611014641', 'source': 'WXO-DD', 'parts': '1,98,1,0,0', 'mtime': '20230611014642.480', 'atime': '20230611014642.480'}

```

The above is the raw sarracenia v02 message as decoded by postformat/v02.py.  the files are downloaded in order to checksum them, and
then after the checksum is done, the files are deleted... the "downloaded" messages appear after the deletion because it actually
represents the end of processing of the file... it was downloaded prior to being deleted.

```
2023-06-10 21:49:41,919 [INFO] sarracenia.flowcb.work.delete after_work deleting /tmp/hpfx_amis/20230611/WXO-DD/bulletins/alphanumeric/20230611/SR/KWAL/01/SRME20_KWAL_110146___33624
2023-06-10 21:49:41,919 [INFO] sarracenia.flowcb.work.delete after_work deleting /tmp/hpfx_amis/20230611/WXO-DD/bulletins/alphanumeric/20230611/SR/KWAL/01/SRCN40_KWAL_110146___17827
2023-06-10 21:49:41,919 [INFO] sarracenia.flowcb.work.delete after_work deleting /tmp/hpfx_amis/20230611/WXO-DD/bulletins/alphanumeric/20230611/SR/KWAL/01/SRCN40_KWAL_110146___33908
2023-06-10 21:49:41,919 [INFO] sarracenia.flowcb.log after_work downloaded ok: /tmp/hpfx_amis/20230611/WXO-DD/bulletins/alphanumeric/20230611/SR/KWAL/01/SRME20_KWAL_110146___33624 
2023-06-10 21:49:41,919 [INFO] sarracenia.flowcb.log after_work downloaded ok: /tmp/hpfx_amis/20230611/WXO-DD/bulletins/alphanumeric/20230611/SR/KWAL/01/SRCN40_KWAL_110146___17827 


```

After the file is processed the new message encoding is published to the local MQTT broker...:

```

2023-06-10 21:49:41,919 [INFO] sarracenia.moth.mqtt putNewMessage Message to publish: topic: origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop body type:<class 'str'> body:{"type": "Feature", "geometry": null,
 "properties": {"integrity": {"method": "sha512", "value": "FUS/Qu8r8xrk3di+sieyuq4WjqNdGXVAoIavdJ0UoRr04X4L0DWz4QYIZ6/F+76Cgq2KXxXlSw8y9kTp9d2SWA=="}, "pubtime": "2023-06-11T01:46:42.480Z", "data_id": "94b4392c-45a1-42ff-96fd-023908ef80
68"}, "version": "v04", "links": [{"rel": "canonical", "href": "https://hpfx.collab.science.gc.ca/20230611/WXO-DD/bulletins/alphanumeric/20230611/SR/KWAL/01/SRME20_KWAL_110146___33624", "length": 98}]}
2023-06-10 21:49:41,921 [INFO] sarracenia.moth.mqtt putNewMessage published mid=1 ack_pending=True {'pubTime': '20230611T014642.480', 'baseUrl': 'https://hpfx.collab.science.gc.ca/', 'relPath': '20230611/WXO-DD/bulletins/alphanumeric/202
30611/SR/KWAL/01/SRME20_KWAL_110146___33624', 'integrity': {'method': 'sha512', 'value': 'FUS/Qu8r8xrk3di+sieyuq4WjqNdGXVAoIavdJ0UoRr04X4L0DWz4QYIZ6/F+76Cgq2KXxXlSw8y9kTp9d2SWA=='}, 'size': 98} to under: origin/a/wis2/can/eccc-msc/data/c
ore/weather/surface-based-observations/synop 

```


To confirm sr3´s ability to ingest messages in WMO/WIS formats, 

Then the subscriber/roundtrip is used to download using the resulting message into /tmp/hpfx_roundtrip:

```bash

ubuntu@flow:~/.cache/sr3/log$ find /tmp/hpfx_roundtrip -type f 
/tmp/hpfx_roundtrip/origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop/be3a84ea-f473-466e-97d7-b11b4b20b8f6
/tmp/hpfx_roundtrip/origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop/94b4392c-45a1-42ff-96fd-023908ef8068
/tmp/hpfx_roundtrip/origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop/7b110a82-9070-49d5-ad7f-37694500c8ed
/tmp/hpfx_roundtrip/origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop/36096f6a-7033-46e6-9c5c-74cd7ca86970
/tmp/hpfx_roundtrip/origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop/2ad2a90e-efac-4b6c-8bf5-003bc7d44a2e
/tmp/hpfx_roundtrip/origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop/da49406d-40b5-488a-bafa-26666b4fbfda
/tmp/hpfx_roundtrip/origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop/f266f8d2-a484-428e-ad59-1a53bfc5f054
/tmp/hpfx_roundtrip/origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop/c2a45119-3efc-478d-a17d-0dacd21dbede
/tmp/hpfx_roundtrip/origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop/c25c5adc-f0d9-4169-9570-18d3ad0cfd53
/tmp/hpfx_roundtrip/origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop/2cf560b4-4bc9-4678-9caf-50ad7a53454e
/tmp/hpfx_roundtrip/origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop/327936cc-738d-4c21-a097-463552013ddd
/tmp/hpfx_roundtrip/origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop/4e4d8038-357a-4de1-bfc6-2e235715fce4
/tmp/hpfx_roundtrip/origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop/e348fc42-3401-4eb3-ae81-e40c8b315514
/tmp/hpfx_roundtrip/origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop/fd28ea32-3dde-4650-a71d-aef8e4d0966a
/tmp/hpfx_roundtrip/origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop/c4788314-0b56-46aa-8571-c0d3f6b4cfa1
ubuntu@flow:~/.cache/sr3/log$ 

```

One can compare the files, but you have to figure out which ones on the download correspond to which at source, which
isn't straightforward.

One can also look at the output of the mosquitto_sub shell to see that the notification messages are in the correct format:

```

.
.
.

{
	"tst":	"2023-06-10T10:13:27.915556Z-0400",
	"topic":	"origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop",
	"qos":	0,
	"retain":	0,
	"payloadlen":	475,
	"payload":	"{\"type\": \"Feature\", \"geometry\": null, \"properties\": {\"integrity\": {\"method\": \"sha512\", \"value\": \"kdQZARwVf7z6jWsbXwLaBqMD7BDBlSf/uQCUHrV9Ix+m1kmWkkX/Miy8BGO97INowXiCL5B/NY5iRRDglcsoQQ==\"}, \"pubtime\": \"2023-06-10T14:12:51.11Z\", \"data_id\": \"ba9b42a1-4397-4f2d-9990-5f23d2022b6d\"}, \"version\": \"v04\", \"links\": [{\"rel\": \"canonical\", \"href\": \"https://hpfx.collab.science.gc.ca/20230610/WXO-DD/bulletins/alphanumeric/20230610/UA/CWAO/14/UANT01_CWAO_101412___53079\", \"length\": 123}]}"
} 
{
	"tst":	"2023-06-10T10:13:27.915837Z-0400",
	"topic":	"origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop",
	"qos":	0,
	"retain":	0,
	"payloadlen":	475,
	"payload":	"{\"type\": \"Feature\", \"geometry\": null, \"properties\": {\"integrity\": {\"method\": \"sha512\", \"value\": \"vFJkP50Yf1Av0DdB/DhlNzFyURW+g+I3+1u5heFVaneKsmXFZWrIhtGmH6v8t7R7vxYW0Z4jcMaCBqpyAwnzKA==\"}, \"pubtime\": \"2023-06-10T14:12:55.17Z\", \"data_id\": \"6713467d-9a64-48fe-8882-37ccbe97ab7b\"}, \"version\": \"v04\", \"links\": [{\"rel\": \"canonical\", \"href\": \"https://hpfx.collab.science.gc.ca/20230610/WXO-DD/bulletins/alphanumeric/20230610/UA/CWAO/14/UANT01_CWAO_101412___63604\", \"length\": 117}]}"
} 

```

