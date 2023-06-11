

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



User Cases
==========

1. Publishing ECCC Datamart data to WMO/WIS data pump.


```base

vmhost%  mkdir ~/.config/sr3/sarra ~/.config/sr3/subscribe
vmhost%  cp config/sr3/subscribe/roundtrip.conf ~/.config/sr3/subscribe
vmhost%  cp config/sr3/sarra/hpfx_amis_to_local_mqtt.conf ~/.config/sr3/sarra
vmhost%  sr3 declare subscribe/roundtrip sarra/hpfx_amis_to_local_mqtt


```

