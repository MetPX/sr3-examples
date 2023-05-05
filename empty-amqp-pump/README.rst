

Given an empty Ubuntu 22.04 (or later) run  the script here:

 ./rabbitmq_pump_setup.sh

to:
  * install metpx-sr3c
  * install metpx-sr3
  * install and configure a rabbitmq message broker.
  * have five basic rabbitmq/amqp users configured:
    * bunnymaster - admin of the rabbitmq broker
    * tfeed - for flows set up by pump administratos.
    * tsource - an account to publish files with
    * tsub - an account to download files with.
    * and anonymous (an account to download using a public password.)

To this empty data pump can be added a lot of other layers of functionality.

To teach people about Sarracenia, can run through the accompanying 
lessons:

* `Sr3 102 Introduction for developers and system administrators <sr3_102_Intro_For_DevsAndAdmins>`_
