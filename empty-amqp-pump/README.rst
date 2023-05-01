
Creation of an empty data pump in a Virtual Machine.


STATUS: In development, not ready yet.

Pre-requisites:

* You have the means of creating a ubuntu 22.04 virtual machine.
  (means of creating a VM are outside the scope of this recipe.)

* You can use your browser to access the ports on the virtual machine.
  (configuring firewalls or routing rules to enable this are outside the scope.)

    

Purpose
-------

In many, many deployment cases, one can use sarracenia without a vm or a local broker.
In fact deploying a broker is a fairly rare need, but to demonstrate what Sarracenia
is, using a broker and a dedicated vm makes things much clearer.

So this example describes how to configure an ubuntu 22.04 virtual machine after
it is obtained. In this example, you will see the simplest possible examples that
demonstrate:

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
* How do you subscribe to a feed?
  * queue
  * topic
  * binding
  * directory
* adjusting file placement.
  * by the subscriber
    * baseDir
  * by the publisher
    * post_baseUrl
    * post_baseDir







In addition, if there is a need for a local broker, then the recipes in this example 
also provide a good starting point. and the tests here allow verification that each
step has worked along the way.




Prepare a Vanilla VM
~~~~~~~~~~~~~~~~~~~~

This section describes creating a test environment for use in a virtual machine. One way to build
a virtual machine is to use multipass (https://multipass.run) Assuming it is installed, one can
create a vm with::

 multipass launch -m 8G -d 30G --name flow

 fractal% multipass list
 Name                    State             IPv4             Image
 flow                    Running           10.110.41.206    Ubuntu 22.04 LTS
 fractal

This will provide a shell in an initialized VM. Get a copy of this repository in the vm::

   git clone https://github.com/MetPX/sr3-examples
   cd empty-amqp-pump

Will install Sarracenia and configure the rabbitmq broker with a few
users. Tha management interface is also active, and one can point
a browser at the broker's management interface.
To configure it::

   rabbitmq_pump_setup.sh

This will generate a lot of output as many dependencies are installed
and rabbitmq is configured. Once it is done, the main pump configuration
directory should look like this::

    ubuntu@flow:~/empty-amqp-pump$ ls -al ~/.config/sr3
    total 20
    drwxrwxr-x 2 ubuntu ubuntu 4096 Apr 30 10:29 .
    drwxrwxr-x 4 ubuntu ubuntu 4096 Apr 30 10:29 ..
    -rw-rw-r-- 1 ubuntu ubuntu  161 Apr 30 10:29 admin.conf
    -rw-rw-r-- 1 ubuntu ubuntu  429 Apr 30 10:29 credentials.conf
    -rw-rw-r-- 1 ubuntu ubuntu  234 Apr 30 10:29 default.conf
    ubuntu@flow:~/empty-amqp-pump$ 
    
The admin.conf file is where user roles are defined::

   ubuntu@flow:~/empty-amqp-pump$ cat ~/.config/sr3/admin.conf
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
VM::

    ubuntu@flow:~/empty-amqp-pump$ ifconfig
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


to log in as admininistrator on the GUI find the password from the credentials file::

    ubuntu@flow:~/empty-amqp-pump$ grep bunnymaster ~/.config/sr3/credentials.conf
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


Then verify that sr3 sees the configurations::

    ubuntu@flow:~/empty-amqp-pump/config/sr3$ sr3 status
    missing state for cpost/my_feed
    status: 
    Component/Config                         Processes   Connection        Lag                Rates                                        
                                             State   Run Retry  msg data   LagMax  LagAvg  %rej     pubsub   messages     RxData     TxData 
                                             -----   --- -----  --- ----   ------  ------  ----   --------       ----     ------     ------ 
    cpost/my_feed                            stop    0/0          -          -         -     -          -        -          -          -          -
    subscribe/hungry                         stop    0/0          -          -         -     -          -        -
          Total Running Configs:   0 ( Processes: 0 missing: 0 stray: 0 )
                         Memory: uss:0 Bytes rss:0 Bytes vms:0 Bytes 
                       CPU Time: User:0.00s System:0.00s 
    	   Pub/Sub Received: 0 msgs/s (0 Bytes/s), Sent:  0 msgs/s (0 Bytes/s)
    	      Data Received: 0 Files/s (0 Bytes/s), Sent: 0 Files/s (0 Bytes/s) 
    ubuntu@flow:~/empty-amqp-pump/config/sr3$ 
    
Have a look at the configurations installed::

    ubuntu@flow:~/empty-amqp-pump/config/sr3$ sr3 edit cpost/my_feed.conf
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


Next step is to tell the broker about these configurations::

    ubuntu@flow:~/empty-amqp-pump/config/sr3$ sr3 declare
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

with sr3 and the broker configured, we can now run the copy.  First step is to start up the subscriber::

    ubuntu@flow:~/empty-amqp-pump/sample$ sr3 start subscribe/hungry
    starting:.( 1 ) Done

    ubuntu@flow:~/empty-amqp-pump/sample$



there is a *samples* directory with a tree of files, one can take a look::

    ubuntu@flow:~/empty-amqp-pump/sample$ find .
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
    
We can post the tree with one command::

    ubuntu@flow:~/empty-amqp-pump/sample$ sr3_cpost -c my_feed -p groceries

which has the output::

    2023-05-01 01:05:24,453 [NOTICE] logEvents option not implemented, ignored.
    2023-05-01 01:05:24,455 [INFO] cpost 3.23.04p2-0~202304252258~ubuntu22.04.1 config: my_feed, pid: 41953, starting
    2023-05-01 01:05:24,468 [INFO] published: { "pubTime":"20230501050524.45545011", "baseUrl":"file:/", "relPath":"home/ubuntu/empty-amqp-pump/sample/groceries", "topic":"v03.post.home.ubuntu.empty-amqp-pump.sample", "mtime":"20230501032604.58783822", "atime":"20230501043538.74174976", "mode":"0775", "fileOp" : { "directory":""}}
    .
    .
    .
    2023-05-01 01:05:24,604 [INFO] published: { "pubTime":"20230501050524.60227867", "baseUrl":"file:/", "relPath":"home/ubuntu/empty-amqp-pump/sample/groceries/dairy/yoghurt/qir", "topic":"v03.post.home.ubuntu.empty-amqp-pump.sample.groceries.dairy.yoghurt", "integrity":{  "method" : "sha512", "value" : "Ortmd680rFfAylgo/ZT52IbCbOWajOYOz2d4B5Qj3M/x1vGctlWAXVYJjm04oacQ3uWVI+7XUR5ank\nuMyzpGhg=="  } , "mtime":"20230501032604.57583808", "atime":"20230501043936.56064233", "mode":"0664", "size":"2"}
    ubuntu@flow:~/empty-amqp-pump/sample$



and then looking at the subscriber log, once can see the messages being received, filtered, and then the files being copied. ::

    ubuntu@flow:~/empty-amqp-pump/sample$ more  ~/.cache/sr3/log/subscribe_hungry_01.log
    
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

We saw the log of the copy above, and we can now look at the file tree created::

    ubuntu@flow:~/empty-amqp-pump/sample$ cd ${HOME}/hungry
    ubuntu@flow:~/hungry$ find .
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

So edit the subscriber configuration and add one of the appropriate lines::

    ubuntu@flow:~/hungry$ rm -rf home
    ubuntu@flow:~/hungry$ sr3 edit subscribe/hungry
    2023-05-01 01:18:03,443 42514 [INFO] sarracenia.sr edit using vi. Set EDITOR variable pick another one.
    
    ubuntu@flow:~/hungry$ sr3 restart subscribe/hungry
    stopping: sending SIGTERM . ( 1 ) Done
    Waiting 1 sec. to check if 1 processes stopped (try: 0)
    Waiting 2 sec. to check if 1 processes stopped (try: 1)
    All stopped after try 1
    starting: .( 1 ) Done
    
    ubuntu@flow:~/hungry$ 
    

And now we can post the files again::

    ubuntu@flow:~/hungry$ sr3_cpost -c my_feed -p /home/ubuntu/empty-amqp-pump/sample/groceries
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
    

And can see what the tree looks like this time::

    ubuntu@flow:~/hungry$ ls
    dairy  fruits  grains  home  meat  nuts  vegetables
    ubuntu@flow:~/hungry$

Much better. But what if we producer knows that no-one is interested in the those upper directories? The producer can signal it
by setting post_baseUrl to include the invariant part, so:

* in cpost/my_feed, change the post_baseUrl line to::

      post_baseUrl file:/home/ubuntu/empty-amqp-pump/sample/groceries


clean up the copied tree::

    ubuntu@flow:~/hungry$ ls
    dairy  fruits  grains  home  meat  nuts  vegetables
    ubuntu@flow:~/hungry$ rm -rf *
    ubuntu@flow:~/hungry$ ls
    ubuntu@flow:~/hungry$ 

edit and post the files again::

    ubuntu@flow:~/hungry$ sr3 edit cpost/my_feed
    2023-05-01 01:38:19,659 43350 [INFO] sarracenia.sr edit using vi. Set EDITOR variable pick another one.
    
    ubuntu@flow:~/hungry$ sr3_cpost -c my_feed -p /home/ubuntu/empty-amqp-pump/sample/groceries
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
Now the messages contain a baseUrl that clearly marks the invariant directories so the subscriber only creates the interesting sub-directories in the download directory::

    ubuntu@flow:~/hungry$ ls -al
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



Install a Web Server
--------------------

On the VM, there is currently just a broker, and announcing files locally does not make them available
to people who cannot log in to the server itself. so install a web server::



Posting Files for Web Retrieval
-------------------------------

* TBD
