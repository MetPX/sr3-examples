

Sarracenia 102: An Empty Data Pump in a Virtual Machine
=======================================================

This example directory contains setup information to make a standalone data pump,
which can be used for other testing.  To prove it works, there are a number of 
included tests that make it work well as a low-level practical introduction to and 
demonstration of Sarracenia for advanced linux users.

No familiarity with Sarracenia or sr3 needed at all. This is a from-scratch introduction. However, to
run this example yourself, you do need the following

Pre-requisites:

* You have the means of creating a ubuntu 22.04 virtual machine.
  (means of creating a VM are outside the scope of this recipe.)

* administrative control over the virtual machine (ability to install and
  configure software.)

* You can use your browser to access the ports on the virtual machine.
  (configuring firewalls or routing rules to enable this are outside the scope.)

* familiarity with linux command line. (ability to type shell commands.)

Ignoring the pedagogical aspect, it can serve as a basis for building other configurations.

Purpose of this Example
-----------------------

In many deployment cases, one can use sarracenia without a vm or a local broker.
In fact deploying a broker is a fairly rare need, but to demonstrate what Sarracenia
is, using a broker and a dedicated vm makes things much clearer.

Here is described how to configure an ubuntu 22.04 virtual machine as a data pump.
In this example, you will see the simplest possible examples that demonstrate:

* What is a broker?

* how do you connect to a broker?

  * broker URL
  * exchange.

* What are sr3 configuration files?

  * format
  * placement
  * meaning.

* How do you post files to a broker?

  * post_baseUrl
  * path

* How do you subscribe to a feed?

  * queue
  * topic
  * binding
  * directory


In addition, if there is a need for a local broker, then the recipes in this example 
also provide a good starting point, and the tests here allow verification that each
step has worked along the way.




Prepare a Vanilla VM
~~~~~~~~~~~~~~~~~~~~

This section describes creating a test environment for use in a virtual machine. One way to build
a virtual machine is to use multipass (https://multipass.run) Assuming it is installed, one can
create a vm with:

 **multipass launch -m 8G -d 30G --name flow**

 fractal% **multipass list**

 ::
 Name                    State             IPv4             Image
 flow                    Running           10.110.41.206    Ubuntu 22.04 LTS
 fractal

This will provide a shell in an initialized VM:

  **multipass shell flow**


Once in a shell on the VM, get a copy of this repository:

   **git clone https://github.com/MetPX/sr3-examples**

   **cd sr3-examples/empty-amqp-pump**

The following script Will install Sarracenia and configure the rabbitmq broker 
with a few users. The management interface will also be active, and one can point
a browser at the broker's management interface.
To configure it:

   **rabbitmq_pump_setup.sh**

This will generate a lot of output as many dependencies are installed
and rabbitmq is configured. Once it is done, the main pump configuration
directory should look like this:

    ubuntu@flow:~/empty-amqp-pump$ **ls -al ~/.config/sr3**

::

    total 20
    drwxrwxr-x 2 ubuntu ubuntu 4096 Apr 30 10:29 .
    drwxrwxr-x 4 ubuntu ubuntu 4096 Apr 30 10:29 ..
    -rw-rw-r-- 1 ubuntu ubuntu  161 Apr 30 10:29 admin.conf
    -rw-rw-r-- 1 ubuntu ubuntu  429 Apr 30 10:29 credentials.conf
    -rw-rw-r-- 1 ubuntu ubuntu  234 Apr 30 10:29 default.conf
    ubuntu@flow:~/empty-amqp-pump$ 
    
The admin.conf file is where user roles are defined:

   ubuntu@flow:~/empty-amqp-pump$ **cat ~/.config/sr3/admin.conf**

::

   admin amqp://bunnymaster@localhost/
   feeder amqp://tfeed@localhost/
   declare source tsource
   declare subscriber tsub
   declare subscriber anonymous
   ubuntu@flow:~/empty-amqp-pump$

So there Are several users defined on the message broker, each one with a password
stored in the ~/.config/sr3/credentials.conf:

* bunnymaster -- the pump administrator, used for monitoring and
  administrative interventions. Not involved in any data flows.

* tfeed - a *feeder* user.  Runs flows configured by pump administrators for the general welfare.

* tsource - a *source* user. Someone publishing products for others to consume.

* tsub - a *subscriber* user.  A user that only consumes products announced by sources or feeders.

* anonymous - a *subsrciber* that everyone knows the password for.


Access the Broker Management Interface
--------------------------------------

RabbitMQ has a management GUI that is makes everything involved in message exchange visible.
RabbitMQ considers the management GUI privileged access, and it is not available to most
publishers and subscribers, but only to thos involved in broker administration.
So one should not expect access to the interface in general, but for this test,
it is helpful to use the Management GUI to see the effect of configuration actions.

To access the management GUI, determine an accessible IP address for your
VM:

    ubuntu@flow:~/empty-amqp-pump$ **ifconfig**

::

    ens3: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.110.41.206  netmask 255.255.255.0  broadcast 10.110.41.255
        inet6 fe80::5054:ff:feca:4297  prefixlen 64  scopeid 0x20<link>
        ether 52:54:00:ca:42:97  txqueuelen 1000  (Ethernet)
        RX packets 103526  bytes 163834555 (163.8 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 29238  bytes 2466353 (2.4 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

    lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 5019  bytes 458589 (458.5 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 5019  bytes 458589 (458.5 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

    ubuntu@flow:~/empty-amqp-pump$


so now if the VM is local, one should be able to access the GUI using the
IP address, and the management port number (15672) url should be something like::

   http://10.110.41.206:15672

And the browser should be something like:

.. image:: Pictures/empty_management_gui.png


to log in as admininistrator on the GUI find the password from the credentials file:

    ubuntu@flow:~/empty-amqp-pump$ **grep bunnymaster ~/.config/sr3/credentials.conf**

::

    amqp://bunnymaster:f2ddc9a71a40@localhost/
    ubuntu@flow:~/empty-amqp-pump$ 

So the password is after the second colon (:) and before the @ in the url. Once
logged in, the normal RabbitMQ GUI should be available:

.. image:: Pictures/Empty_Management_Gui_Logged_In.png

You can see the users created in the management GUI

.. image:: Pictures/Mgmt_GUI_Users.png

And see the permissions set up for users to match their roles:

.. image:: Pictures/Mgmt_GUI_tsource_detail.png


Testing Local File Posting
---------------------------

Now we can try out the broker by posting files on the server
for another process to subsribe to and copy to another directory.
copy the configurations we need to the active ones::

    cd config/sr3
    for d in *; do
       mkdir -p ~/.config/sr3/$d
    done
    for cfg in */*; do
       cp ${cfg} ~/.config/sr3/${cfg}
       echo copied ${cfg}
    done

Should see output like::


    copied cpost/my_feed.conf
    copied subscribe/hungry.conf


Then verify that sr3 sees the configurations:

    ubuntu@flow:~/empty-amqp-pump/config/sr3$ **sr3 status**

::

    missing state for cpost/my_feed
    status:
    Component/Config                         Processes   Connection        Lag                Rates
                                             State   Run Retry  msg data   LagMax  LagAvg  %rej     pubsub   messages     RxData     TxData
                                             -----   --- -----  --- ----   ------  ------  ----   --------       ----     ------     ------
    cpost/my_feed                            stop    0/0          -          -         -     -          -        -          -          -          -
    sarra/web_feed                           stop    0/0          -          -         -     -          -        -
    subscribe/hungry                         stop    0/0          -          -         -     -          -        -
    subscribe/web_hungry                     stop    0/0          -          -         -     -          -        -
      Total Running Configs:   0 ( Processes: 0 missing: 0 stray: 0 )
                     Memory: uss:0 Bytes rss:0 Bytes vms:0 Bytes
                   CPU Time: User:0.00s System:0.00s
	   Pub/Sub Received: 0 msgs/s (0 Bytes/s), Sent:  0 msgs/s (0 Bytes/s)
	      Data Received: 0 Files/s (0 Bytes/s), Sent: 0 Files/s (0 Bytes/s)
    ubuntu@flow:~/sr3-examples/empty-amqp-pump/config/sr3$
    
Have a look at the configurations installed:

    ubuntu@flow:~/empty-amqp-pump/config/sr3$ **sr3 edit cpost/my_feed.conf**

::

    2023-04-30 23:52:38,041 38333 [INFO] sarracenia.sr edit using vi. Set EDITOR variable pick another one.
    ubuntu@flow:~/empty-amqp-pump/config/sr3$

contents of the file is::

    post_broker amqp://tsource@localhost
    post_exchange xs_tsource_public
    post_baseUrl file:/


This is the configuration file for *sr3_cpost* which is a program that is given paths to be posted 
as arguments on the command line. If a directory is given on the command line, then it is recursively
descended. For each file in the tree given, a message is created, and sent to the message broker.
The first line of configuration *post_broker* specifies which broker to connect to, and using which account.
All of the variables have *post\_* prefix to indicate that they are for publishing (aka posting) of messages.

The broker has named channels called *exchanges*.  Some exchanges are built-in, while others can be declared.
the publisher selects the exchange to publish on, and the subscriber must use the same channel if it
wants to receive them.

The second configuration file's ( subscribe/hungry ) contents is::

   broker amqp://tsub@localhost

   exchange xs_tsource_public

   mirror
   directory ${HOME}/hungry


a *broker* is a one used for to create a subscription (to listen for messages.)
the *exchange* needs to match what the poster is posting.
The *directory* option says where to copy the files to.  Mirroring is a flag (on or off) 
used to tell it to make the tree under ${HOME}/hungry look like the source tree.
If mirroring is off, all files are going to just be placed in ${HOME}/hungry.


Next step is to tell the broker about these configurations:

    ubuntu@flow:~/empty-amqp-pump/config/sr3$ **sr3 declare**

::

    declare: 2023-05-01 00:11:19,344 39126 [INFO] root declare looking at cpost/my_feed
    2023-05-01 00:11:19,358 39126 [INFO] sarracenia.moth.amqp __putSetup exchange declared: xs_tsource_public (as: amqp://tsource@localhost/)
    2023-05-01 00:11:19,359 39126 [INFO] root declare looking at subscribe/hungry
    2023-05-01 00:11:19,359 39126 [INFO] root declare looking at cpost/my_feed
    2023-05-01 00:11:19,359 39126 [INFO] root declare looking at subscribe/hungry
    2023-05-01 00:11:19,365 39126 [INFO] sarracenia.moth.amqp __getSetup queue declared q_tsub_subscribe.hungry.92090753.33857788 (as: amqp://tsub@localhost/)
    2023-05-01 00:11:19,365 39126 [INFO] sarracenia.moth.amqp __getSetup binding q_tsub_subscribe.hungry.92090753.33857788 with v03.# to xs_tsource_public (as: amqp://tsub@localhost/)
    
    ubuntu@flow:~/empty-amqp-pump/config/sr3$
    

One can now look in the management GUI for:

* the exchange created for the publisher,
* the queue created for the subscriber.
* the binding between the two.


First the exchanges:

.. image:: Pictures/Mgmt_GUI_Exchanges.png

Note the xs_tsource_public exchange has been added (because of the post_exchange declaration in cpost/my_feed )

Then the queues:

.. image:: Pictures/Mgmt_GUI_Queues.png

When a subscriber is declared, a queue for it must be created on the broker to hold messages published until
they are picked up by the subscriber. Sr3 guesses at a reasonable name, and adds some randomised sequences
to the end to allow multiple declarations using the same broker not to clash.

.. image:: Pictures/Mgmt_GUI_Queue_Detail.png

Clicking on the queue for more detail, one can see that a how the publisher and subscriber are related to
each other on the broker.  A *binding* of the queue has been created to the posters channel (xs_tsource_public.) 
It has a routing key of *v03.#*. The period (.) is a topic separator, and the hash or number sign is a wildcard 
to match any topic, so this binding means: *match all messages published to the broker whose topic starts with v03.*

An sr3 program that posts create notification messages in v03 format by default, and part of v03 format includes setting it's
topic to start with v03 as the first element. so that means that the subscriber's queue is bound to receive every
message published by our poster.

with sr3 and the broker configured, we can now run the copy. First step is to start up the subscriber:



there is a *samples* directory with a tree of files, one can take a look:

    ubuntu@flow:~/empty-amqp-pump/sample$ **find .**

::

    .
    ./groceries
    ./groceries/grains
    ./groceries/grains/bread
    ./groceries/grains/bread/whole_wheat
    ./groceries/grains/bread/shinken_brot
    .
    .
    .
    ./groceries/dairy/yoghurt
    ./groceries/dairy/yoghurt/blueberry
    ./groceries/dairy/yoghurt/mango
    ./groceries/dairy/yoghurt/raspberry
    ./groceries/dairy/yoghurt/qir
    ubuntu@flow:~/empty-amqp-pump/sample$
    
We can post the tree with one command:

    ubuntu@flow:~/empty-amqp-pump/sample$ **sr3_cpost -c my_feed -p groceries**

which has the output::

    2023-05-01 01:05:24,453 [NOTICE] logEvents option not implemented, ignored.
    2023-05-01 01:05:24,455 [INFO] cpost 3.23.04p2-0~202304252258~ubuntu22.04.1 config: my_feed, pid: 41953, starting
    2023-05-01 01:05:24,468 [INFO] published: { "pubTime":"20230501050524.45545011", "baseUrl":"file:/", "relPath":"home/ubuntu/empty-amqp-pump/sample/groceries", "topic":"v03.post.home.ubuntu.empty-amqp-pump.sample", "mtime":"20230501032604.58783822", "atime":"20230501043538.74174976", "mode":"0775", "fileOp" : { "directory":""}}
    .
    .
    .
    2023-05-01 01:05:24,604 [INFO] published: { "pubTime":"20230501050524.60227867", "baseUrl":"file:/", "relPath":"home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt/qir", "topic":"v03.post.home.ubuntu.empty-amqp-pump.sample.groceries.dairy.yoghurt", "integrity":{  "method" : "sha512", "value" : "Ortmd680rFfAylgo/ZT52IbCbOWajOYOz2d4B5Qj3M/x1vGctlWAXVYJjm04oacQ3uWVI+7XUR5ank\nuMyzpGhg=="  } , "mtime":"20230501032604.57583808", "atime":"20230501043936.56064233", "mode":"0664", "size":"2"}
    ubuntu@flow:~/empty-amqp-pump/sample$


so the posting happenned, and since the queue is declared we can go and look on the broker,
and see all the messages queued for this subscriber.



    ubuntu@flow:~/empty-amqp-pump/sample$ **sr3 start subscribe/hungry**

::

    starting:.( 1 ) Done

    ubuntu@flow:~/empty-amqp-pump/sample$


and then looking at the subscriber log, once can see the messages being received, filtered, and then the files being copied.:

    ubuntu@flow:~/empty-amqp-pump/sample$ **more  ~/.cache/sr3/log/subscribe_hungry_01.log**

::
    
    2023-05-01 01:03:14,822 [INFO] sarracenia.flowcb.log on_housekeeping housekeeping
    2023-05-01 01:05:24,569 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 0.11 ) file:/ home/ubuntu/empty-amqp-pump/sample/groceries
    2023-05-01 01:05:24,569 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 0.10 ) file:/ home/ubuntu/empty-amqp-pump/sample/groceries/grains
    2023-05-01 01:05:24,569 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 0.10 ) file:/ home/ubuntu/empty-amqp-pump/sample/groceries/grains/bread
    2023-05-01 01:05:24,569 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 0.10 ) file:/ home/ubuntu/empty-amqp-pump/sample/groceries/grains/bread/whole_w
    heat
    .
    .
    .

    2023-05-01 01:05:24,750 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 0.15 ) file:/ home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt/raspbe
    rry
    2023-05-01 01:05:24,750 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 0.15 ) file:/ home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt/qir
    2023-05-01 01:05:24,760 [INFO] sarracenia.flowcb.log after_work downloaded ok: /home/ubuntu/hungry/home/ubuntu/empty-amqp-pump/sample/groceries/dairy/milk/homo
    2023-05-01 01:05:24,760 [INFO] sarracenia.flowcb.log after_work directory ok: /home/ubuntu/hungry/home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt
    2023-05-01 01:05:24,760 [INFO] sarracenia.flowcb.log after_work downloaded ok: /home/ubuntu/hungry/home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt/yop
    lay_0fat_0sugar_all_chemical
    2023-05-01 01:05:24,760 [INFO] sarracenia.flowcb.log after_work downloaded ok: /home/ubuntu/hungry/home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt/blu
    eberry
    2023-05-01 01:05:24,760 [INFO] sarracenia.flowcb.log after_work downloaded ok: /home/ubuntu/hungry/home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt/man
    go
    2023-05-01 01:05:24,760 [INFO] sarracenia.flowcb.log after_work downloaded ok: /home/ubuntu/hungry/home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt/ras
    pberry
    2023-05-01 01:05:24,760 [INFO] sarracenia.flowcb.log after_work downloaded ok: /home/ubuntu/hungry/home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt/qir
    
    ubuntu@flow:~/empty-amqp-pump/sample$
    
.. NOTE:

   If there is nothing in the subscriber log, then the binding does not match what the publisher was posting.  
   Check the "topic" header in the messages. If they start with "v02.post" instead of v03, then it's just a bug where older
   versions of the C use the old "v02" format by default (where releases >= v3.23.05 use v03 by default) you might 
   need to edit the cpost file to add::

        post_topicPrefix v03



        
Adjusting Download Paths
------------------------

We saw the log of the copy above, and we can now look at the file tree created:

    ubuntu@flow:~/empty-amqp-pump/sample$ **cd ${HOME}/hungry**

    ubuntu@flow:~/hungry$ **find .**

::

    .
    ./home
    ./home/ubuntu
    ./home/ubuntu/empty-amqp-pump
    ./home/ubuntu/empty-amqp-pump/sample
    ./home/ubuntu/empty-amqp-pump/sample/groceries
    ./home/ubuntu/empty-amqp-pump/sample/groceries/grains
    .
    .
    .

    ./home/ubuntu/empty-amqp-pump/sample/groceries/grains/bread
    ./home/ubuntu/empty-amqp-pump/sample/groceries/dairy/milk/soy
    ./home/ubuntu/empty-amqp-pump/sample/groceries/dairy/milk/1percent
    ./home/ubuntu/empty-amqp-pump/sample/groceries/dairy/milk/homo
    ./home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt
    ./home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt/yoplay_0fat_0sugar_all_chemical
    ./home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt/blueberry
    ./home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt/mango
    ./home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt/raspberry
    ./home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt/qir
    ubuntu@flow:~/hungry$ 
    

We can see it re-created the entire path run under the directory where we placed it.
Perhaps we don't want an exact mirror. If we know we have a number of un-interesting 
directories at the root of the tree we are downloading adjust the tree in a 
number of ways

* Using baseDir to specify exactly what to omit::

   baseDir /home/ubuntu/empty-amqp-pump/sample/groceries

* Using strip to specify a number of directories to strip from the root of the path::

   strip 5

So edit the subscriber configuration and add one of the appropriate lines:

    ubuntu@flow:~/hungry$ **rm -rf home**

    ubuntu@flow:~/hungry$ **sr3 edit subscribe/hungry**

::

    2023-05-01 01:18:03,443 42514 [INFO] sarracenia.sr edit using vi. Set EDITOR variable pick another one.
    
    ubuntu@flow:~/hungry$ sr3 restart subscribe/hungry
    stopping: sending SIGTERM . ( 1 ) Done
    Waiting 1 sec. to check if 1 processes stopped (try: 0)
    Waiting 2 sec. to check if 1 processes stopped (try: 1)
    All stopped after try 1
    starting: .( 1 ) Done
    
    ubuntu@flow:~/hungry$ 
    

And now we can post the files again:

    ubuntu@flow:~/hungry$ **sr3_cpost -c my_feed -p /home/ubuntu/empty-amqp-pump/sample/groceries**

::

    2023-05-01 01:20:54,651 [NOTICE] logEvents option not implemented, ignored.
    2023-05-01 01:20:54,653 [INFO] cpost 3.23.04p2-0~202304252258~ubuntu22.04.1 config: my_feed, pid: 42637, starting
    2023-05-01 01:20:54,664 [INFO] published: { "pubTime":"20230501052054.65344578", "baseUrl":"file:/", "relPath":"home/ubuntu/empty-amqp-pump/sample/groceries", "topic":"v03.post.home.ubuntu.empty-amqp-pump.sample", "mtime":"20230501032604.58783822", "atime":"20230501043538.74174976", "mode":"0775", "fileOp" : { "directory":""}}
    2023-05-01 01:20:54,667 [INFO] published: { "pubTime":"20230501052054.66479594", "baseUrl":"file:/", "relPath":"home/ubuntu/empty-amqp-pump/sample/groceries/grains", "topic":"v03.post.home.ubuntu.empty-amqp-pump.sample.groceries", "mtime":"20230501032604.58383817", "atime":"20230501043538.74174976", "mode":"0775", "fileOp" : { "directory":""}}
    2023-05-01 01:20:54,670 [INFO] published: { "pubTime":"20230501052054.66768656", "baseUrl":"file:/", "relPath":"home/ubuntu/empty-amqp-pump/sample/groceries/grains/bread", "topic":"v03.post.home.ubuntu.empty-amqp-pump.sample.groceries.grains", "mtime":"20230501032604.57983812", "atime":"20230501043538.74174976", "mode":"0775", "fileOp" : { "directory":""}}
    2023-05-01 01:20:54,672 [INFO] published: { "pubTime":"20230501052054.67015332", "baseUrl":"file:/", "relPath":"home/ubuntu/empty-amqp-pump/sample/groceries/grains/bread/whole_wheat", "topic":"v03.post.home.ubuntu.empty-amqp-pump.sample.groceries.grains.bread", "integrity":{  "method" : "sha512", "value" : "V5EVHm08ogoiJGYin3
    .
    .
    .
    
    23-05-01 01:20:54,783 [INFO] published: { "pubTime":"20230501052054.78199497", "baseUrl":"file:/", "relPath":"home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt/raspberry", "topic":"v03.post.home.ubuntu.empty-amqp-pump.sample.groceries.dairy.yoghurt", "integrity":{  "method" : "sha512", "value" : "YVYeCdTNKDTzcUAwyW8p1qoW56s1BRyRrb/fPukLrVwstoXWjldjJdFvUhgIrVYPpnygUUkFZC6jQZ\n6XTV5Ykw=="  } , "mtime":"20230501032604.57583808", "atime":"20230501043936.55664228", "mode":"0664", "size":"2"}
    2023-05-01 01:20:54,784 [INFO] published: { "pubTime":"20230501052054.7830358", "baseUrl":"file:/", "relPath":"home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt/qir", "topic":"v03.post.home.ubuntu.empty-amqp-pump.sample.groceries.dairy.yoghurt", "integrity":{  "method" : "sha512", "value" : "Ortmd680rFfAylgo/ZT52IbCbOWajOYOz2d4B5Qj3M/x1vGctlWAXVYJjm04oacQ3uWVI+7XUR5ank\nuMyzpGhg=="  } , "mtime":"20230501032604.57583808", "atime":"20230501043936.56064233", "mode":"0664", "size":"2"}
    ubuntu@flow:~/hungry$
    

And can see what the tree looks like this time:

    ubuntu@flow:~/hungry$ **ls**

::
    dairy  fruits  grains  home  meat  nuts  vegetables
    ubuntu@flow:~/hungry$

Much better. But what if we producer knows that no-one is interested in the those upper directories? The producer can signal it
by setting post_baseUrl to include the invariant part, so:

* in cpost/my_feed, change the post_baseUrl line to::

      post_baseUrl file:/home/ubuntu/empty-amqp-pump/sample/groceries


clean up the copied tree:

    ubuntu@flow:~/hungry$ **ls**

    dairy  fruits  grains  home  meat  nuts  vegetables

    ubuntu@flow:~/hungry$ **rm -rf ***

    ubuntu@flow:~/hungry$ **ls**

    ubuntu@flow:~/hungry$ 

edit and post the files again:

    ubuntu@flow:~/hungry$ **sr3 edit cpost/my_feed**

    2023-05-01 01:38:19,659 43350 [INFO] sarracenia.sr edit using vi. Set EDITOR variable pick another one.

    ubuntu@flow:~/hungry$ **sr3_cpost -c my_feed -p /home/ubuntu/empty-amqp-pump/sample/groceries**

::

    2023-05-01 01:38:48,948 [NOTICE] logEvents option not implemented, ignored.
    2023-05-01 01:38:48,949 [INFO] cpost 3.23.04p2-0~202304252258~ubuntu22.04.1 config: my_feed, pid: 43386, starting
    2023-05-01 01:38:48,962 [INFO] published: { "pubTime":"20230501053848.94989936", "baseUrl":"file:/home/ubuntu/empty-amqp-pump/sample/groceries", "relPath":"", "top
    .
    .
    .
    2023-05-01 01:38:49,080 [INFO] published: { "pubTime":"20230501053849.07917617", "baseUrl":"file:/home/ubuntu/empty-amqp-pump/sample/groceries", "relPath":"dairy/yoghurt/raspberry", "topic":"v03.post.dairy.yoghurt", "integrity":{  "method" : "sha512", "value" : "YVYeCdTNKDTzcUAwyW8p1qoW56s1BRyRrb/fPukLrVwstoXWjldjJdFvUhgIrVYPpnygUUkFZC6jQZ\n6XTV5Ykw=="  } , "mtime":"20230501032604.57583808", "atime":"20230501043936.55664228", "mode":"0664", "size":"2"}
    2023-05-01 01:38:49,081 [INFO] published: { "pubTime":"20230501053849.08040859", "baseUrl":"file:/home/ubuntu/empty-amqp-pump/sample/groceries", "relPath":"dairy/yoghurt/qir", "topic":"v03.post.dairy.yoghurt", "integrity":{  "method" : "sha512", "value" : "Ortmd680rFfAylgo/ZT52IbCbOWajOYOz2d4B5Qj3M/x1vGctlWAXVYJjm04oacQ3uWVI+7XUR5ank\nuMyzpGhg=="  } , "mtime":"20230501032604.57583808", "atime":"20230501043936.56064233", "mode":"0664", "size":"2"}
    ubuntu@flow:~/hungry$
    
    
This time the subscriber does not need a *strip* or a *baseDir* setting because the poster has split things up nicely.
Now the messages contain a baseUrl that clearly marks the invariant directories so the subscriber only creates the interesting sub-directories in the download directory:

    ubuntu@flow:~/hungry$ **ls -al**

::

    total 32
    drwxrwxr-x 8 ubuntu ubuntu 4096 May  1 01:38 .
    drwxr-x--- 8 ubuntu ubuntu 4096 May  1 01:38 ..
    drwxrwxr-x 5 ubuntu ubuntu 4096 May  1 01:38 dairy
    drwxrwxr-x 6 ubuntu ubuntu 4096 May  1 01:38 fruits
    drwxrwxr-x 6 ubuntu ubuntu 4096 May  1 01:38 grains
    drwxrwxr-x 2 ubuntu ubuntu 4096 May  1 01:38 meat
    drwxrwxr-x 2 ubuntu ubuntu 4096 May  1 01:38 nuts
    drwxrwxr-x 2 ubuntu ubuntu 4096 May  1 01:38 vegetables
    ubuntu@flow:~/hungry$

ok, then stop the subscriber, as we are done with this example:

    ubuntu@flow:~/.config/sr3/sarra$ **sr3 stop subscribe/hungry**

::

    Stopping: sending SIGTERM . ( 1 ) Done
    Waiting 1 sec. to check if 1 processes stopped (try: 0)
    Waiting 2 sec. to check if 1 processes stopped (try: 1)
    All stopped after try 1
   
   ubuntu@flow:~/.config/sr3/sarra$ 
   


Install a Web Server
--------------------

On the VM, there is currently just a broker, and announcing files locally does not make them available
to people who cannot log in to the server itself. so install a web server:

    ubuntu@flow:~$ **sudo apt install apache2**

::

    Reading package lists... Done
    Building dependency tree... Done
    Reading state information... Done
    The following additional packages will be installed:
      apache2-bin apache2-data apache2-utils libapr1 libaprutil1 libaprutil1-dbd-sqlite3 libaprutil1-ldap liblua5.3-0 mailcap mime-support ssl-cert
    Suggested packages:
      apache2-doc apache2-suexec-pristine | apache2-suexec-custom www-browser
    The following NEW packages will be installed:
      apache2 apache2-bin apache2-data apache2-utils libapr1 libaprutil1 libaprutil1-dbd-sqlite3 libaprutil1-ldap liblua5.3-0 mailcap mime-support ssl-cert
    0 upgraded, 12 newly installed, 0 to remove and 0 not upgraded.
    Need to get 2102 kB of archives.
    After this operation, 8389 kB of additional disk space will be used.
    Do you want to continue? [Y/n] y
    Get:1 http://archive.ubuntu.com/ubuntu jammy-updates/main amd64 libapr1 amd64 1.7.0-8ubuntu0.22.04.1 [108 kB]
    Get:2 http://archive.ubuntu.com/ubuntu jammy-updates/main amd64 libaprutil1 amd64 1.6.1-5ubuntu4.22.04.1 [92.6 kB]
    Get:3 http://archive.ubuntu.com/ubuntu jammy-updates/main amd64 libaprutil1-dbd-sqlite3 amd64 1.6.1-5ubuntu4.22.04.1 [11.3 kB]
    Get:4 http://archive.ubuntu.com/ubuntu jammy-updates/main amd64 libaprutil1-ldap amd64 1.6.1-5ubuntu4.22.04.1 [9168 B]
    Get:5 http://archive.ubuntu.com/ubuntu jammy/main amd64 liblua5.3-0 amd64 5.3.6-1build1 [140 kB]
    Get:6 http://archive.ubuntu.com/ubuntu jammy-updates/main amd64 apache2-bin amd64 2.4.52-1ubuntu4.5 [1345 kB]
    Get:7 http://archive.ubuntu.com/ubuntu jammy-updates/main amd64 apache2-data all 2.4.52-1ubuntu4.5 [165 kB]
    Get:8 http://archive.ubuntu.com/ubuntu jammy-updates/main amd64 apache2-utils amd64 2.4.52-1ubuntu4.5 [89.1 kB]
    Get:9 http://archive.ubuntu.com/ubuntu jammy/main amd64 mailcap all 3.70+nmu1ubuntu1 [23.8 kB]
    Get:10 http://archive.ubuntu.com/ubuntu jammy/main amd64 mime-support all 3.66 [3696 B]
    Get:11 http://archive.ubuntu.com/ubuntu jammy-updates/main amd64 apache2 amd64 2.4.52-1ubuntu4.5 [97.8 kB]
    Get:12 http://archive.ubuntu.com/ubuntu jammy/main amd64 ssl-cert all 1.1.2 [17.4 kB]
    Fetched 2102 kB in 1s (1603 kB/s)
    Preconfiguring packages ...
    Selecting previously unselected package libapr1:amd64.
    (Reading database ... 75012 files and directories currently installed.)
    Preparing to unpack .../00-libapr1_1.7.0-8ubuntu0.22.04.1_amd64.deb ...
    Unpacking ...
    .
    .
    .
    Scanning processes...
    Scanning linux images...
    
    Running kernel seems to be up-to-date.
    
    No services need to be restarted.
    
    No containers need to be restarted.
    
    No user sessions are running outdated binaries.
    
    No VM guests are running outdated hypervisor (qemu) binaries on this host.
    ubuntu@flow:~$
    
So now, if you point your browser at http://10.110.41.206, you should see an "Apache2 Default Page"
saying "It works!"

By default, the root of the tree is /var/www.html. so to make it usable to retrieve files with, 
create a writeable sub-directory for our use:

   ubuntu@flow:~$ **sudo mkdir /var/www/html/data**

   ubuntu@flow:~$ **sudo chown ${USER} /var/www/html/data**

   ubuntu@flow:~$ **ls -al /var/www/html/data**

::

   total 8
   drwxr-xr-x 2 ubuntu root 4096 May  1 10:52 .
   drwxr-xr-x 3 root   root 4096 May  1 10:52 ..
   ubuntu@flow:~$
    
And now you can browse there and see an empty directory:

.. image:: Pictures/web_browser_empty.png



Posting Files for Web Retrieval
-------------------------------
    
So we have a data source producing files locally (cpost/my_feed) and we want to make those
products available to other servers.

We can use a sarra configuration to copy the files into the web tree, and then repost
them for web clients.


Here is what that configuration looks like::

    
    broker amqp://tsub@localhost
    
    exchange xs_tsource_public
    
    # make directories to match the source.
    mirror
    
    
    # root of the directory where published files are placed.
    directory /var/www/html/data/groceries
    
    # above here is the same as a simple subscriber...
    
    # after downloading, we want to publish the downloaded files
    # for others, so we are also a poster:
    
    post_broker amqp://tfeed@localhost
    post_exchange xpublic
    
    #The URL used for people to download
    post_baseUrl http://10.110.41.206/data/groceries
    
To log into the post_broker, we use the administrative *tfeed* user (role: feeder)
because ordinary sources are not allowed to post to the *xpublic* exchange.

    
We start this sarra, and then repost the files with sr3_cpost just
like was done for the subscriber:
    
    
    ubuntu@flow:~/.config/sr3/cpost$ **sr3 start sarra/web_feed**

    starting:.( 1 ) Done
    
    ubuntu@flow:~/.config/sr3/cpost$ **set -o vi**

    ubuntu@flow:~/.config/sr3/cpost$ **sr3_cpost -c my_feed -p /home/ubuntu/empty-amqp-pump/sample/groceries**

::

    2023-05-01 11:21:03,501 [NOTICE] logEvents option not implemented, ignored.
    2023-05-01 11:21:03,503 [INFO] cpost 3.23.04p2-0~202304261849~ubuntu22.04.1 config: my_feed, pid: 4004, starting
    2023-05-01 11:21:03,515 [INFO] published: { "pubTime":"20230501152103.50350649", "baseUrl":"file:/home/ubuntu/empty-amqp-pump/sample/groceries", "relPath":"", "topic":"v03.post", "mtime":"20230501032604.58783822", "atime":"20230501043538.74174976", "mode":"0775", "fileOp" : { "directory":""}}
    2023-05-01 11:21:03,518 [INFO] published: { "pubTime":"20230501152103.51531606", "baseUrl":"file:/home/ubuntu/empty-amqp-pump/sample/groceries", "relPath":"grains", "topic":"v03.post", "mtime":"20230501032604.58383817", "atime":"20230501043538.74174976", "mode":"0775", "fileOp" : { "directory":""}}
    2023-05-01 11:21:03,522 [INFO] published: { "pubTime":"20230501152103.5188737", "baseUrl":"file:/home/ubuntu/empty-amqp-pump/sample/groceries", "relPath":"grains
    .
    .
    . (omitting the rest of the posts which should be the same as before.)
    
    
With the sarra running, bound to what the cpost publishes just like the subscriber, it will download the files
and put them in the directory that the web server can see. If we look at the log, we will see entries like::

    .
    .
    .
    
    023-05-01 11:20:46,853 [INFO] sarracenia.flowcb.log __init__ sarra initialized with: {'on_housekeeping', 'after_post', 'post', 'after_accept', 'after_work'}
    2023-05-01 11:20:46,854 [INFO] sarracenia.flow run callbacks loaded: ['sarracenia.flowcb.post.message.Message', 'sarracenia.flowcb.gather.message.Message', 'sarr
    acenia.flowcb.retry.Retry', 'sarracenia.flowcb.housekeeping.resources.Resources', 'log']
    2023-05-01 11:20:46,854 [INFO] sarracenia.flow run pid: 3973 sarra/web_feed instance: 1
    2023-05-01 11:20:46,854 [INFO] sarracenia.flow run now active on vip None
    2023-05-01 11:21:03,871 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 0.37 ) file:/home/ubuntu/empty-amqp-pump/sample/groceries
    2023-05-01 11:21:03,871 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 0.36 ) file:/home/ubuntu/empty-amqp-pump/sample/groceries grains
    2023-05-01 11:21:03,871 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 0.35 ) file:/home/ubuntu/empty-amqp-pump/sample/groceries grains/bread
    .
    .
    .
    023-05-01 11:21:03,871 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 0.31 ) file:/home/ubuntu/empty-amqp-pump/sample/groceries vegetables/garlic
    2023-05-01 11:21:03,918 [INFO] sarracenia.flowcb.log after_work directory ok: /var/www/html/data/groceries/
    2023-05-01 11:21:03,918 [INFO] sarracenia.flowcb.log after_work directory ok: /var/www/html/data/groceries/grains
    2023-05-01 11:21:03,918 [INFO] sarracenia.flowcb.log after_work directory ok: /var/www/html/data/groceries/grains/bread
    2023-05-01 11:21:03,918 [INFO] sarracenia.flowcb.log after_work downloaded ok: /var/www/html/data/groceries/grains/bread/whole_wheat
    2023-05-01 11:21:03,918 [INFO] sarracenia.flowcb.log after_work downloaded ok: /var/www/html/data/groceries/grains/bread/shinken_brot
    2023-05-01 11:21:03,918 [INFO] sarracenia.flowcb.log after_work downloaded ok: /var/www/html/data/groceries/grains/bread/Wonder
    2023-05-01 11:21:03,918 [INFO] sarracenia.flowcb.log after_work downloaded ok: /var/www/html/data/groceries/grains/bread/white
    .
    .
    .
    
    2023-05-01 11:21:03,924 [INFO] sarracenia.flowcb.log after_post posted {'_format': 'v03', '_deleteOnPost': {'new_dir', '_format', 'local_offset', 'subtopic', 'ne
    w_file', 'report', 'new_baseUrl', 'new_inflight_path', 'new_subtopic', 'post_format', 'new_path', 'onfly_checksum', 'data_checksum', 'new_relPath', 'timeComplete
    d', 'exchange'}, 'pubTime': '20230501T152103.5293704', 'baseUrl': 'http://10.110.41.206/data/groceries', 'relPath': 'var/www/html/data/groceries/grains/bread/Won
    der', 'integrity': {'method': 'sha512', 'value': 'pHX6NeXjAaiwmdF1Ioe84Hvx7IjJhMcaGPIFUDPsyUZ/NkLNIYTVUXpIe4np7oKNTA1LzLOtGcXQjo\nYq+xbCpQ=='}, 'source': 'tsourc
    e', 'size': 3, 'atime': '20230501T043936.53664204', 'mtime': '20230501T032604.57983812', 'mode': '664', 'exchange': 'xs_tsource_public', 'subtopic': ['var', 'www
    ', 'html', 'data', 'groceries', 'grains', 'bread'], 'local_offset': 0, 'new_dir': '/var/www/html/data/groceries/grains/bread', 'new_file': 'Wonder', 'post_format
    ': 'v03', 'new_baseUrl': 'http://10.110.41.206/data/groceries', 'new_relPath': 'var/www/html/data/groceries/grains/bread/Wonder', 'new_subtopic': ['var', 'www',
    'html', 'data', 'groceries', 'grains', 'bread'], 'new_inflight_path': 'Wonder', 'new_path': '/var/www/html/data/groceries/grains/bread/Wonder', 'onfly_checksum':
     {'method': 'sha512', 'value': 'pHX6NeXjAaiwmdF1Ioe84Hvx7IjJhMcaGPIFUDPsyUZ/NkLNIYTVUXpIe4np7oKNTA1LzLOtGcXQjoYq+xbCpQ=='}, 'data_checksum': 'z4PhNX7vuL3xVChQ1m2
    AB9Yg5AULVxXcg/SpIdNs6c5H0NE8XYXysP+DGNKHfuwvY7kxvUdBeoGlODJ6+SfaPg==', 'timeCompleted': '20230501T152103.889377117', 'report': {'code': 201, 'message': 'Downloa
    d successful /var/www/html/data/groceries/grains/bread/Wonder'}}
    
This shows the three phases of sarra running:

* Gather & filter: it receives messages from the broker, selects or filters them and then "accepts" them.
* Work: It copies them to where they are supposed to go.
* Post: It posts messages modified so they refer to the new copies.  

If we go visit web browser, the files are there:

.. image:: Pictures/web_browser_withData.png

So now the files are present on the web server, test it by downloading from the web.
Here is a second subscriber made to download from what sarra published: 
     
     broker amqp://anonymous@localhost
     
     exchange xpublic
     
     # make directories to match the source.
     mirror
     
     # root of the directory where files will be placed.
     directory ${HOME}/web_hungry
     
This is now using an anonymous user to subscribe to the xpublic exchange, and place the files it is told
about to the web_hungry directory. Starting that up:

    ubuntu@flow:~/.config/sr3/subscribe$ **sr3 start subscribe/web_hungry**

::

    starting:.( 1 ) Done

    ubuntu@flow:~/.config/sr3/subscribe$ 

    ubuntu@flow:~/.config/sr3/subscribe$ sr3 status
    status:
    Component/Config                         Processes   Connection        Lag                Rates
                                         State   Run Retry  msg data   LagMax  LagAvg  %rej     pubsub   messages     RxData     TxData
                                         -----   --- -----  --- ----   ------  ------  ----   --------       ----     ------     ------
    cpost/my_feed                            stop    0/0          -          -         -     -          -        -
    sarra/web_feed                           run     1/1     0 100%   0% 1201.27s 1201.20s 78.0%  7.5 KiB/s  18 msgs/s  0 Bytes/s  0 Bytes/s
    subscribe/hungry                         stop    0/0     0  -1%   0%    0.00s    0.00s  0.0%  0 Bytes/s   0 msgs/s  0 Bytes/s  0 Bytes/s
    subscribe/web_hungry                     run     1/1     0 100%   0% 1202.02s 1201.96s  0.0% 12 Bytes/s   0 msgs/s  0 Bytes/s  0 Bytes/s
          Total Running Configs:   2 ( Processes: 2 missing: 0 stray: 0 )
                         Memory: uss:45.8 MiB rss:69.1 MiB vms:87.3 MiB
                       CPU Time: User:0.44s System:0.14s
    	   Pub/Sub Received: 7.6 Kim/s (7.6 KiB/s), Sent:  4 msgs/s (4 Bytes/s)
    	      Data Received: 4 Files/s (0 Bytes/s), Sent: 0 Files/s (0 Bytes/s)
    ubuntu@flow:~/.config/sr3/subscribe$
    
If we look at the logs, they are empty. Why? because we started up the subscriber after the files were
posted, so there was no queue declared on the broker in which to accumulate messages.  To get
this subscriber to see the messages, we can just post them again with sr3_cpost as above:

    ubuntu@flow:~/.config/sr3/cpost$ **sr3_cpost -c my_feed -p /home/ubuntu/empty-amqp-pump/sample/groceries**

::

    .
    .
    . (same local file posts as before.)

the files get copied by sarra/web_feed, then posted to *xpublic*, so the subscriber should see them.
We look at ${HOME}/web_hungry, we see a tree of directories, with for example::

    /home/ubuntu/web_hungry/var/www/html/data/groceries/fruits/pears

If we go back and look at the messages, we can see that the files were announced with the following fields::

    'new_baseUrl': 'http://10.110.41.206/data/groceries', 
    'new_relPath': 'var/www/html/data/groceries/grains/bread/Wonder

When the subscriber receives a message, it will concatenate the two together to generate the download URL::

    http://10.110.41.206/data/groceries/var/www/html/data/groceries/grains/bread/Wonder

but that retrieve will fail because the actual path on the web server is::

    http://10.110.41.206/data/groceries/grains/bread/Wonder

So the directory announced by the web server is different from the aboluste path that we write the file
info.  To fix that, we add to the sarra/web_feed configuration::

   post_baseDir /var/www/html/data/groceries

to indicate what sarra should remove from the path when publishing:

    ubuntu@flow:~/.config/sr3/subscribe$ **sr3 edit sarra/web_feed**

    2023-05-01 12:30:51,282 6822 [INFO] sarracenia.sr edit using vi. Set EDITOR variable pick another one.
    
    ubuntu@flow:~/.config/sr3/subscribe$

    ubuntu@flow:~/.config/sr3/subscribe$ **sr3 restart sarra/web_feed**

::

    stopping: sending SIGTERM . ( 1 ) Done
    Waiting 1 sec. to check if 2 processes stopped (try: 0)
    Waiting 2 sec. to check if 2 processes stopped (try: 1)
    All stopped after try 1
    starting: .( 1 ) Done
    
    ubuntu@flow:~/.config/sr3/subscribe$
    
Then post the files again, and still no files are being written by subscribe/web_hungry.  In fact there are not even
files in the log at all. If we check the *sr3 status* :

    ubuntu@flow:~/.config/sr3/sarra$ **sr3 status**

::

    status:
    Component/Config                         Processes   Connection        Lag                Rates
                                             State   Run Retry  msg data   LagMax  LagAvg  %rej     pubsub   messages     RxData     TxData
                                             -----   --- -----  --- ----   ------  ------  ----   --------       ----     ------     ------
    cpost/my_feed                            stop    0/0          -          -         -     -          -        -
    sarra/web_feed                           run     1/1     0 100%   0%    2.57s    2.51s 78.0% 472 Bytes/s   1 msgs/s  0 Bytes/s  0 Bytes/s
    subscribe/hungry                         stop    0/0     0  -1%   0%    0.00s    0.00s  0.0%  0 Bytes/s   0 msgs/s  0 Bytes/s  0 Bytes/s
    subscribe/web_hungry                     run     1/1     0 100%   0%    4.72s    4.66s  0.0% 44 Bytes/s   0 msgs/s  0 Bytes/s  0 Bytes/s
          Total Running Configs:   2 ( Processes: 2 missing: 0 stray: 0 )
                         Memory: uss:45.8 MiB rss:69.1 MiB vms:87.3 MiB
                       CPU Time: User:0.22s System:0.05s
    	   Pub/Sub Received: 516 msgs/s (516 Bytes/s), Sent:  0 msgs/s (0 Bytes/s)
    	      Data Received: 0 Files/s (0 Bytes/s), Sent: 0 Files/s (0 Bytes/s)
    ubuntu@flow:~/.config/sr3/sarra$
    
If you see the sarra/web_feed is running, but looking at the %rej column, it is rejecting 78% of the messages it receives. hmm... the other
22% is probably directories, lets see why it is rejecting those files:

    ubuntu@flow:~/.config/sr3/sarra$ **sr3 edit sarra/web_feed.conf**

::

    2023-05-01 12:51:16,485 7695 [INFO] sarracenia.sr edit using vi. Set EDITOR variable pick another one.

    ubuntu@flow:~/.config/sr3/sarra$

    (  Add a line with logReject, so that sarra writes a log message explaining why it rejected messages. )

We repost the messages (sr3_cpost like before) the messages and then look in the sarra log:

   
   ubuntu@flow:~/empty-amqp-pump/sample$ **sr3_cpost -c my_feed -p groceries**

   .

   .

   .

   ubuntu@flow:~/.config/sr3/sarra$ **grep rejected ~/.cache/sr3/log/sarra_web_feed_01.log | head**

::

   2023-05-01 12:46:38,575 [INFO] sarracenia.flowcb.log after_work rejected: 304 mtime not newer /var/www/html/data/groceries/grains/bread/whole_wheat  
   2023-05-01 12:46:38,575 [INFO] sarracenia.flowcb.log after_work rejected: 304 mtime not newer /var/www/html/data/groceries/grains/bread/shinken_brot  
   2023-05-01 12:46:38,575 [INFO] sarracenia.flowcb.log after_work rejected: 304 mtime not newer /var/www/html/data/groceries/grains/bread/Wonder  
   2023-05-01 12:46:38,575 [INFO] sarracenia.flowcb.log after_work rejected: 304 mtime not newer /var/www/html/data/groceries/grains/bread/white  
   2023-05-01 12:46:38,575 [INFO] sarracenia.flowcb.log after_work rejected: 304 mtime not newer /var/www/html/data/groceries/grains/flour/whole_wheat  
   2023-05-01 12:46:38,575 [INFO] sarracenia.flowcb.log after_work rejected: 304 mtime not newer /var/www/html/data/groceries/grains/flour/white  
   2023-05-01 12:46:38,575 [INFO] sarracenia.flowcb.log after_work rejected: 304 mtime not newer /var/www/html/data/groceries/grains/grains/hops  
   2023-05-01 12:46:38,575 [INFO] sarracenia.flowcb.log after_work rejected: 304 mtime not newer /var/www/html/data/groceries/grains/grains/barley  
   2023-05-01 12:46:38,575 [INFO] sarracenia.flowcb.log after_work rejected: 304 mtime not newer /var/www/html/data/groceries/grains/grains/malt  
   2023-05-01 12:46:38,575 [INFO] sarracenia.flowcb.log after_work rejected: 304 mtime not newer /var/www/html/data/groceries/grains/pasta/tagliatelle  
   ubuntu@flow:~/.config/sr3/sarra$ 
   
So, when files are sent between many different machines, it is common for "loops" to occur. To tamp down on loops, a usual strategy
is duplicate suppression (implemented by the *sarracenia.flowcb.nodupe.NoDupe* class in sr3) A full discussion is out of scope here, but
at this time we just want to turn it off:
    
    ubuntu@flow:~/.config/sr3/sarra$ **sr3 stop sarra/web_feed**

    Stopping: sending SIGTERM . ( 1 ) Done

    Waiting 1 sec. to check if 2 processes stopped (try: 0)

    All stopped after try 0
    
    ubuntu@flow:~/.config/sr3/sarra$ **rm ~/.cache/sr3/log/***

    ubuntu@flow:~/.config/sr3/sarra$ **sr3 start sarra/web_feed**

    starting:.( 1 ) Done
    
    ubuntu@flow:~/.config/sr3/sarra$

Then post again:

   ubuntu@flow:~/empty-amqp-pump/sample$ **sr3_cpost -c my_feed -p groceries**

::

   .
   .
   .

and look for rejects again:

   ubuntu@flow:~/.config/sr3/sarra$  **grep rejected ~/.cache/sr3/log/sarra_web_feed_01.log | head**

   ubuntu@flow:~/.config/sr3/sarra$ 

so now it still complains about the mtime::

   2023-05-03 06:58:33,436 [INFO] sarracenia.flowcb.log after_work rejected: 304 mtime not newer /var/www/html/data/groceries/dairy/milk/skim
   2023-05-03 06:58:33,436 [INFO] sarracenia.flowcb.log after_work rejected: 304 mtime not newer /var/www/html/data/groceries/dairy/milk/soy
   2023-05-03 06:58:33,436 [INFO] sarracenia.flowcb.log after_work rejected: 304 mtime not newer /var/www/html/data/groceries/dairy/milk/1percent

So the issue is that, since the files have already been copied from the source to under /var/www/html, the files
already downloaded aren't any different from what is being posted. If the files aren't new, then the sarra
process will not forward them (duplicate suppression.) so we delete all the files that the sarra/web_feed has
written:

   ubuntu@flow:~/.config/sr3/sarra$ **rm -rf /var/www/html/data/groceries**

then we can start again:

   ubuntu@flow:~/.config/sr3/sarra$ **sr3 stop**

   ubuntu@flow:~/.config/sr3/sarra$ **sr3 cleanup**

   ubuntu@flow:~/.config/sr3/sarra$ **sr3 start sarra/web_feed subscribe/web_hungry**

   ubuntu@flow:~/empty-amqp-pump/sample$ **sr3_cpost -c my_feed -p groceries**

And now, if we look at the subscribe/web_feed log::

    ubuntu@flow:~/.cache/sr3/log$ tail -f subscribe_web_hungry_01.log
    .
    .
    .
    2023-05-03 00:02:35,661 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 5.47 ) http://10.110.41.206/data/groceries dairy/milk/homo
    2023-05-03 00:02:35,661 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 5.47 ) http://10.110.41.206/data/groceries dairy/yoghurt
    2023-05-03 00:02:35,661 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 5.47 ) http://10.110.41.206/data/groceries dairy/yoghurt/yoplay_0fat_0sugar_all_chemical
    2023-05-03 00:02:35,661 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 5.47 ) http://10.110.41.206/data/groceries dairy/yoghurt/blueberry
    2023-05-03 00:02:35,661 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 5.47 ) http://10.110.41.206/data/groceries dairy/yoghurt/mango
    2023-05-03 00:02:35,661 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 5.46 ) http://10.110.41.206/data/groceries dairy/yoghurt/raspberry
    2023-05-03 00:02:35,661 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 5.46 ) http://10.110.41.206/data/groceries dairy/yoghurt/qir
    2023-05-03 00:02:35,673 [INFO] sarracenia.flowcb.log after_work downloaded ok: /home/ubuntu/web_hungry/dairy/milk/homo
    2023-05-03 00:02:35,673 [INFO] sarracenia.flowcb.log after_work directory ok: /home/ubuntu/web_hungry/dairy/yoghurt
    2023-05-03 00:02:35,673 [INFO] sarracenia.flowcb.log after_work downloaded ok: /home/ubuntu/web_hungry/dairy/yoghurt/yoplay_0fat_0sugar_all_chemical
    2023-05-03 00:02:35,673 [INFO] sarracenia.flowcb.log after_work downloaded ok: /home/ubuntu/web_hungry/dairy/yoghurt/blueberry
    2023-05-03 00:02:35,673 [INFO] sarracenia.flowcb.log after_work downloaded ok: /home/ubuntu/web_hungry/dairy/yoghurt/mango


It shows that we are seeing the download url's and then successfully downloading the corresponding files.
If we inspect the subscribe/web_hungry's output directory, we see that it successfully
copied the entire tree:

    ubuntu@flow:~$ *cd*

    ubuntu@flow:~$ *find web_hungry -type f*

:: 

    web_hungry/grains/bread/whole_wheat
    web_hungry/grains/bread/shinken_brot
    web_hungry/grains/bread/Wonder
    web_hungry/grains/bread/white
    web_hungry/grains/flour/whole_wheat
    web_hungry/grains/flour/white
    web_hungry/grains/grains/hops
    web_hungry/grains/grains/barley
    .
    .
    .
    web_hungry/dairy/yoghurt/raspberry
    web_hungry/dairy/yoghurt/qir
    ubuntu@flow:~$
    


Review
------

* we can use **sr3_cpost** to create json messages about files and send them to a *broker*

* a *message broker* is software that matches what publishers with the expressed interests (or *bindings* ) of subscribers.

  * We use rabbitmq as a broker, publish to an exchange (like a television channel )

  * A subscriber will declare a queues, and bindings it to exchanges to match interests.

* Sarracenia processes are managed with configuration files

  * that are placed in a structured tree under *~/.config/sr3*.
  * *default.conf* .. configuration settings to be used by all others.
  * and *credentials.conf* ... contains authentication information, mostly as urls.
  *  is a directory for each "component": e.g.:   cpost, subscribe, sarra

    * A component sets some defaults for a configuration.

  * each file in those directories sets how a linux process (or group of them) will run.
  
 * Sarracenia has logs in ~/.cache/sr3/log

 * Sarracenis stores state in other files under ~/.cache/sr3/

   *example: ~/.cache/sr3/subscribe/web_hungry/*retry*

* there is a command line interface to working with the entire configuration tree at once:

  * **sr3 status**  - snapshot of what is currently going on.
  * **sr3 start/stop/restart** - manage the processes to run.
  * **sr3 cleanup**  - delete server side resources.

  by default, it operates on everything under *~/.config/sr3*. One can give configurations on the 
  command line to operate on only a subset of the configurations listed by sr3 status.


* The message contains a location in two parts: baseUrl, and relPath. eg:

  * "baseUrl": "http://10.110.41.206/data/groceries",
  * "relPath": "dairy/yoghurt/qir"

  The two fields are combined to create a download Url. the baseUrl can be any Url, and
  usually indicates how the file is retrieved. Sarracenia currently supports: file: http: and sftp:
  urls.
 
* sr_cpost is an example of a publisher.
  A publisher needs to choose how to publish a path to get the baseUrl and relPath right.
  its configuration would include options like:

  * post_broker (a url) the server to publish to.
  * post_exchange (a name) a sort of named channel to publish messages to.
  * post_baseUrl - the baseUrl that will be in the message.
  * post_baseDir - remove this part of the path when publishing the url

  example:

  * / to the apache web server is /var/www/html, so that must be at least part of post_baseDir

  * we create files under there, such as /var/www/html/data/groceries/dairy/milk/soy

  * the complete Url for retrieval is: http://10.110.41.206/data/groceries/dairy/milk/soy
    it could be divided in a number of different ways. We chose to split at the "groceries"
    level.

  * so post_baseUrl = http://10.110.41.206/data/groceries ... the static part of the URL 
  * so post_baseDir = /var/www/html/data/groceries to match it.


* When downloading, the following configuration file options are important:

  options: 

  * broker (a url) the server the look for messages
  * exchange (a name) where the message have been published.
  * *directory* -- when mirroring a tree, start with a root where we want to write it
  * *strip* -- Removes some levels of directories from the beginning of the relative path.
       Sometimes we want to copy only part of a tree, and some intervening directories 
       aren't relevant.

* A sarra component is an example of a complete flow. It:

  * consumes messages (posted by the cpost) from its broker queue.
  * copies the files to the right place under the web server.
  * modifies the messages for the files, so that subscribers can download from the web server.
  * publishes those messages back to the broker (on another *exchange* or channel)

  All Sarracenia components follow the same *flow*::

  * gather  - subscribe to a message source, or look at a file system to generate messages.
  * filter  - drop some messages from the gathered list.
  * work    - to some file transfer or transformation.
  * post    - adjust the messages and post the result for consumers from this.

  Sarracenia configurations daisy chain together to achieve multi-hop processing.
