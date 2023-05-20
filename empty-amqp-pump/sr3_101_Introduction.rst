
===========
Start Here
===========

This set of materials is hosted here: 

* https://github.com/MetPX/sr3-examples

Everything done in these examples should be reproducible by others.


Sarracenia in 10 minutes
------------------------

* Original "Project Scope" video, made in 2015 before the Sarracenia existed.

* The general idea: https://www.youtube.com/watch?v=G47DRwzwckk

* It was written before Sarracenia existed. It showed the plan.
  opportunities and deployments followed since then.


What Got Dropped
-----------------
 
* website moved: https://metpx.github.io/sarracenia
* have not had demand/use cases for: segmented files.
  * prioritization, to be re-implemented in time.
* have not deployed: reports (easy to do, but high volume.)
  * prioritization: easily re-implemented.
* cluster level routing: people want specific data sets, not all data from a cluster.
  * easily re-implemented.
* Edmonton site was dismantled (Project Alta)
* RADAR redundancy was implemented and then dismantled (S-Band only upload to Montreal)
    

What Stayed
-----------

* pub/sub with urls 
* daisy chain of servers to cross network barriers (placed near demarcation points)
* flexible mass file transfers at high speed (parallelism with instances.)
* multiple deployments of winnowing (HA with checksums.)
  * e.g. URP now winnows among six servers!
  * lots of issues with winnowing methods.


What's "new" (vs. 2015)
-----------------------

* "Sources" groupings of data by originating org (replaced cluster routing.)
* Python plugin API, addreses initial inflexibilities.
* extensive python re-factor from 2020-2023 resulting in sr3 (Sarracenia version 3)
  * 20% code size reduction
  * one algorithm for all components, and more commonality and consistency.
  * MQTT (another queueing protocol besides AMQP.)
  * different, more pythonic plugin architecture
* The C implementation exists and is integrated so both can be used together
  * subset (components: post,watch + shovel )
  * typically 10x lighter/faster than python, but no API.
  * the HPC mirroring use case. (not covered here.)

Sarracenia Components
----------------------

.. image:: Pictures/sr3_flow_example.svg


Vocabulary
-----------


.. image:: Pictures/AMQP4Sarra.svg



