

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

To teach people in depth about Sarracenia, one can run through the accompanying 
tours:

* `Sr3 102: Introduction for Developers and System Administrators <sr3_102_Intro_For_DevsAndAdmins.rst>`_

Documentation:

* All the options (the verbs in the configuration files) https://metpx.github.io/sarracenia/Reference/sr3_options.7.html

* The command line: https://metpx.github.io/sarracenia/Reference/sr3.1.html

* The missing sr3 101 course: https://metpx.github.io/sarracenia/Tutorials/1_CLI_introduction.html

* Sarracenia/sr3 home page: https://metpx.github.io/sarracenia/


