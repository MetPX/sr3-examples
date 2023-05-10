
Sr3 103 Selecting Files for Processing
======================================

status: Outline

Downloading
-----------

Setup
~~~~~

1. create an empty ubuntu 22.04 VM.

   * Follow the recip <README.rst> for create an empty data pump.

   * note the ip of the vm, and open a browser window on the management GUI (port 15672)
     the password for the bunnymaster user is in ~/.config/sr3/credentials.conf

2. copy the example configurations over:

   copy the configurations we need to the active ones::

    cd config/sr3
    for d in *; do
       mkdir -p ~/.config/sr3/$d
    done
    for cfg in */*; do
       cp ${cfg} ~/.config/sr3/${cfg}
       echo copied ${cfg}
    done

3. Declare the resources for local file post and subscription.


   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3 declare cpost/my_feed subscribe/hungry**

::

    declare: 2023-05-08 15:36:48,365 7791 [INFO] root declare looking at cpost/my_feed
    2023-05-08 15:36:48,379 7791 [INFO] sarracenia.moth.amqp __putSetup exchange declared: xs_tsource_public (as: amqp://tsource@localhost/)
    2023-05-08 15:36:48,380 7791 [INFO] root declare looking at subscribe/hungry
    2023-05-08 15:36:48,380 7791 [INFO] root declare looking at cpost/my_feed
    2023-05-08 15:36:48,380 7791 [INFO] root declare looking at subscribe/hungry
    2023-05-08 15:36:48,385 7791 [INFO] sarracenia.moth.amqp __getSetup queue declared q_tsub_subscribe.hungry.39945722.38576406 (as: amqp://tsub@localhost/)
    2023-05-08 15:36:48,385 7791 [INFO] sarracenia.moth.amqp __getSetup binding q_tsub_subscribe.hungry.39945722.38576406 with v03.# to xs_tsource_public (as: amqp://tsub@localhost/)

    ubuntu@flow2:~/sr3-examples/empty-amqp-pump$

4.  First pass, edit to get a reasonable root of the posting tree

    * edit the my_feed post_baseUrl to be more practical (longer one)
      (comment out the first one in the file, uncomment the second one.)

      ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3 edit cpost/my_feed**

5. Post the files.

ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3_cpost -c my_feed -p ~/sr3-examples/empty-amqp-pump/sample**

    ::

        2023-05-08 15:53:25,724 [NOTICE] logEvents option not implemented, ignored.
        2023-05-08 15:53:25,726 [INFO] cpost 3.23.05~ubuntu22.04.1 config: my_feed, pid: 8456, starting
        2023-05-08 15:53:25,726 [ERROR] posting outside of post_baseDir (/home/ubuntu/sr3-examples/empty-amqp-pump/sample/groceries) invalid path: /home/ubuntu/sr3-examples/empty-amqp-pump/sample
        2023-05-08 15:53:25,739 [INFO] published: { "pubTime":"20230508195325.72626993", "baseUrl":"file:/home/ubuntu/sr3-examples/empty-amqp-pump/sample/groceries", "relPath":"", "topic":"v03.post", "mtime":"20230508184339.48218706", "atime":"20230508194318.74930167", "mode":"0775", "fileOp" : { "directory":""}}
        2023-05-08 15:53:25,742 [INFO] published: { "pubTime":"20230508195325.73984278", "baseUrl":"file:/home/ubuntu/sr3-examples/empty-amqp-pump/sample/groceries", "relPath":"grains", "topic":"v03.post", "mtime":"20230508184339.48218706", "atime":"20230508194318.74930167", "mode":"0775", "fileOp" : { "directory":""}}
        2023-05-08 15:53:25,744 [INFO] published: { "pubTime":"20230508195325.74221365", "baseUrl":"file:/home/ubuntu/sr3-examples/empty-amqp-pump/sample/groceries", "relPath":"gr
        .
        .
        .

so because the declare was done above all of these files are now in the queue for the subscribe/hungry
configuration.  Looking at the management UI, Select the Queue tab, and then the queue itself 
within the tab, and then, looking down the list "get Message" and perhaps 5 as a quantity,
should give you a display similar to::

.. image: Pictures/sb103_messages_in_queue_screenshot.png

Note that, RabbitMQ does not use or understand the content of a message.
The messages are opaque binaries to RabbitMQ (or any AMQP broker.) 
Brokers use only the envelope information, or metadata of a message 
to do routing. Above each message in the display below is some metadata:

 * *Exchange*:  which exchange the message was published to in order to get into this queue.

 * *Routing Key*  With Sarracenia, all the exchanges used are *topic exchanges* so the *routing key* is a topic.

When sr3_cpost created the message, it assigned a topic header, by starting with the topic prefix (default: 'v03.post') 
and then appending the directories in the relative path of the message. Note that in AMQP, the topic separator
is a period, so the slashes are replaced by periods.

The messages are in one line, here is a version with a few line breaks for readability::

   { 
       "pubTime" : "20230508T195325.7449953", 
       "baseUrl" : "file:/home/ubuntu/sr3-examples/empty-amqp-pump/sample/groceries", 
       "relPath" : "grains/bread/whole_wheat", 
       "integrity" : {  
                "method" : "sha512", 
                "value" : "V5EVHm08ogoiJGYin3qlhpzWf6kssgqB7+KNkLd+QOibwQ8EQ5wcaRALZf1NDX/xZgAdsPRZ4mtLU2\nm6CHCQnw=="  
       },
       "source" : "tsource", 
       "size" : "3", 
       "atime" : "20230508T194318.74930167", 
       "mtime" : "20230508T184339.48218706", 
       "mode" : "664" 
   }

The path the subscriber will use to download is the concatenation of the *baseUrl* and and *relPath*
fields. In this message the relative path (from the "relPath" field) is "grains/bread/whole_wheat" ...  
 
* Topic will be: v03.post.grains.bread
* whole_wheat is the file name (only directories are in the topic)


the subscriber has no information about the topic in it. but the default topicPrefix is v03.post,
and the default subtopic is #.  # is a wildcard to any combination of topics, so the main binding
which can bee seen in the rabbitmq display is to:

   xs_tsource_public  v03.post.#

which essentially means every file posted by sr3_cpost. (> 80 of them.)


Using subtopic
~~~~~~~~~~~~~~

Topic filtering reduces the number of unwanted messages downloaded by a client
for Example:

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3 stop subscribe/hungry**

      * stop the download subscription daemon.

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3 cleanup subscribe/hungry**

      * discard the old queue contents, delete the old queue.

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3 edit subscribe/hungry**

      * add a line *topicPrefix v03.post*
      * add a line *subtopic fruits.#* 

   so that the hungry subscription is only interested in getting fruits

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3 declare subscribe/hungry**

      * create a new queue, with the new binding.  
      * can see the new biding in the management gui for the new queue.

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3_cpost -c my_feed -p ~/sr3-examples/empty-amqp-pump/sample**

      * posting the files again.


Now examining the queue again, we see that far fewer files are queued for the subscriber (less than 30.)

This *server-side filtering*, is done by the broker itself, avoiding the transfer of messages between
broker and subscriber.  This is the most efficient means of filtering messages, however:

* one can only include topic to be included, there is no way to specify exclusions.
* the topic tree includes folder names, no filtering by file name is possible.

so when we start up the subscriber:

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3 start subscribe/hungry**

::

   starting:.( 1 ) Done

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ 

will then download only the fruits directory from the all the directories posted by cpost:

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$  **cd ~/hungry**

   ubuntu@flow2:~/hungry$ **find `pwd`**

::

    /home/ubuntu/hungry
    /home/ubuntu/hungry/fruits
    /home/ubuntu/hungry/fruits/mango.qty
    /home/ubuntu/hungry/fruits/oranges
    /home/ubuntu/hungry/fruits/oranges/valencia.qty
    /home/ubuntu/hungry/fruits/oranges/blood.jpg
    /home/ubuntu/hungry/fruits/oranges/cara_cara.jpg
    /home/ubuntu/hungry/fruits/oranges/clementine.qty
    /home/ubuntu/hungry/fruits/oranges/mandarins.jpg
    /home/ubuntu/hungry/fruits/oranges/clementines.jpg
    /home/ubuntu/hungry/fruits/oranges/mandarin.qty
    /home/ubuntu/hungry/fruits/oranges/cara_cara.qty
    /home/ubuntu/hungry/fruits/oranges/blood.qty
    /home/ubuntu/hungry/fruits/oranges/navel.qty
    /home/ubuntu/hungry/fruits/apples
    /home/ubuntu/hungry/fruits/apples/empire_qc.qty
    /home/ubuntu/hungry/fruits/apples/granny_smith.jpg
    /home/ubuntu/hungry/fruits/apples/empire.qty
    /home/ubuntu/hungry/fruits/apples/granny_smith.qty
    /home/ubuntu/hungry/fruits/apples/cortland.jpg
    /home/ubuntu/hungry/fruits/apples/macinthosh_qc.qty
    /home/ubuntu/hungry/fruits/apples/red_delicious.qty
    /home/ubuntu/hungry/fruits/bananas
    /home/ubuntu/hungry/fruits/bananas/cavendish.qty
    /home/ubuntu/hungry/fruits/bananas/plantain.qty
    /home/ubuntu/hungry/fruits/bananas/red_banana.qty
    /home/ubuntu/hungry/fruits/bananas/goldfinger.qty
    /home/ubuntu/hungry/fruits/bananas/pisang_raja_indonesia.qty
    /home/ubuntu/hungry/fruits/pears
    /home/ubuntu/hungry/fruits/pears/asian.qty
    /home/ubuntu/hungry/fruits/pears/yellow_snow.qty
    /home/ubuntu/hungry/fruits/pears/bartlett.qty
    ubuntu@flow2:~/hungry$

So these are the files available in the fruits directory.

* Most of these files are qty files.
* if we are only interested in the images, we should reject the qty files.


   ubuntu@flow2:~/hungry$ **rm -rf fruits**

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3 stop subscribe/hungry**

      * stop the download subscription daemon.

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3 edit subscribe/hungry**

      * add a line *reject .\*.qty*

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3 cleanup subscribe/hungry**

      * discard the old queue contents, delete the old queue.

   ubuntu@flow2:~/hungry$ **sr3 declare subscribe/hungry** ::

     declare: 2023-05-08 17:50:28,196 13249 [INFO] root declare looking at subscribe/hungry
     2023-05-08 17:50:28,196 13249 [INFO] root declare looking at subscribe/hungry
     2023-05-08 17:50:28,212 13249 [INFO] sarracenia.moth.amqp __getSetup queue declared q_tsub_subscribe.hungry.34148622.02913293 (as: amqp://tsub@localhost/)
     2023-05-08 17:50:28,212 13249 [INFO] sarracenia.moth.amqp __getSetup binding q_tsub_subscribe.hungry.34148622.02913293 with v03.post.fruits.# to xs_tsource_public (as: amqp://tsub@localhost/)

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3_cpost -c my_feed -p ~/sr3-examples/empty-amqp-pump/sample**
   
      * post the files again.

   If we now consult the management GUI, we shoould see on the order of 20 files in the queue.
   like before.  If we then:

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3 start subscribe/hungry**

      * start the download subscription daemon, with the new reject line.

   ubuntu@flow2:~/hungry$ find `pwd`
   /home/ubuntu/hungry
   /home/ubuntu/hungry/fruits
   /home/ubuntu/hungry/fruits/oranges
   /home/ubuntu/hungry/fruits/oranges/blood.jpg
   /home/ubuntu/hungry/fruits/oranges/cara_cara.jpg
   /home/ubuntu/hungry/fruits/oranges/mandarins.jpg
   /home/ubuntu/hungry/fruits/oranges/clementines.jpg
   /home/ubuntu/hungry/fruits/apples
   /home/ubuntu/hungry/fruits/apples/granny_smith.jpg
   /home/ubuntu/hungry/fruits/apples/cortland.jpg
   /home/ubuntu/hungry/fruits/bananas
   /home/ubuntu/hungry/fruits/pears
   ubuntu@flow2:~/hungry$ 


So now we see that while there were >20 files queued on the broker, the subscriber only copied a handful of files,
the ones that were not rejected.

Accept/Reject Clauses
~~~~~~~~~~~~~~~~~~~~~

* Apply additional filtering to include or exclude files from the set to be transferred

* work with full regular expressions, not just globbing or string matching.

* Rather than being evaluated on the broker, done on the client (inside sarracenia programes.)
  messages are downloaded prior to evaluation, but the files data is not (yet) transferred

* The accept/reject clauses work on the full URL, that is, in this case, they would have see paths like:

       file:/home/ubuntu/sr3-examples/empty-amqp-pump/sample/groceries/fruits/apples/cortland.jpg

* are the main part of the *filter* in the sarracenia algorithm, that is part of the flow of each
  sarracenia sr_subscribe process, 
  
* if a file is accepted, processing continues, and the corresponding file gets transferred.


Multiple Directories 
~~~~~~~~~~~~~~~~~~~~

The configuration file is read from top to bottom, and some options can appear multiple
times. If there are multiple *accept* and *reject* clauses, know that the first one
to match the input URL will be actioned.

The *directory* clause sets the root of stuff to be download, *for accept clauses that follow 
it in the file* (or the end of file if there are none.) The mirror option works has the 
same scope, affecting files accepted later in the file.

 if we edit web_hungry to look like this ::

    broker amqp://tsub@localhost

    exchange xs_tsource_public

    topicPrefix v03.post
    subtopic fruits.#
    subtopic vegetables.#

    # print log messages for every file rejected.
    logReject on

    # make directories to match the source.
    mirror off

    reject .*\.qty

    # root of the directory where files will be placed.

    directory ${HOME}/hungry/fruits
    accept .*fruits.*

    mirror on
    directory ${HOME}/hungry/

We have turned off mirroring, and now want both fruits and vegetables in their
own directories.

We can demonstrate that with another round:


   ubuntu@flow2:~/hungry$ **rm -rf fruits**

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3 stop subscribe/hungry**

      * stop the download subscription daemon.

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3 edit subscribe/hungry**

      * as illustrated above:
      * add line "subtopic vegetables.#
      * change mirror off
      * add line "directory ${HOME}/hungry/fruits 
      * add line "accept .*/fruits/.*
      * add line mirror on

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3 cleanup subscribe/hungry**

      * discard the old queue contents, delete the old queue.

   ubuntu@flow2:~/hungry$ **sr3 declare subscribe/hungry** ::

     declare: 2023-05-09 08:10:31,448 48412 [INFO] root declare looking at subscribe/hungry
     2023-05-09 08:10:31,448 48412 [INFO] root declare looking at subscribe/hungry
     2023-05-09 08:10:31,462 48412 [INFO] sarracenia.moth.amqp __getSetup queue declared q_tsub_subscribe.hungry.49018002.48697803 (as: amqp://tsub@localhost/)
     2023-05-09 08:10:31,462 48412 [INFO] sarracenia.moth.amqp __getSetup binding q_tsub_subscribe.hungry.49018002.48697803 with v03.post.fruits.# to xs_tsource_public (as: amqp://tsub@localhost/)
     2023-05-09 08:10:31,465 48412 [INFO] sarracenia.moth.amqp __getSetup binding q_tsub_subscribe.hungry.49018002.48697803 with v03.post.vegetables.# to xs_tsource_public (as: amqp://tsub@localhost/)

the we post and subscribe

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3_cpost -c my_feed -p ~/sr3-examples/empty-amqp-pump/sample**
   
      * post the files again.

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3 start subscribe/hungry**

      * start the download subscription daemon, with the new reject line.

   ubuntu@flow2:~/hungry$ find `pwd` ::

     /home/ubuntu/hungry
     /home/ubuntu/hungry/vegetables
     /home/ubuntu/hungry/vegetables/brussel_sprouts.qty
     /home/ubuntu/hungry/vegetables/boston_lettuce.qty
     /home/ubuntu/hungry/vegetables/tomatoes.qty
     /home/ubuntu/hungry/vegetables/roots
     /home/ubuntu/hungry/vegetables/roots/garlic.qty
     /home/ubuntu/hungry/vegetables/roots/chives.qty
     /home/ubuntu/hungry/vegetables/roots/potatoes
     /home/ubuntu/hungry/vegetables/roots/potatoes/idaho_red.qty
     /home/ubuntu/hungry/vegetables/roots/potatoes/cavendish.qty
     /home/ubuntu/hungry/vegetables/roots/potatoes/irish.qty
     /home/ubuntu/hungry/vegetables/roots/potatoes/sweet.qty
     /home/ubuntu/hungry/vegetables/roots/carrots.qty
     /home/ubuntu/hungry/vegetables/roots/onions.jpg
     /home/ubuntu/hungry/vegetables/roots/onions.qty
     /home/ubuntu/hungry/vegetables/roots/shallots.jpg
     /home/ubuntu/hungry/vegetables/roots/potatoes.qty
     /home/ubuntu/hungry/vegetables/roots/shallots.qty
     /home/ubuntu/hungry/vegetables/broccoli.qty
     /home/ubuntu/hungry/vegetables/spinach.qty
     /home/ubuntu/hungry/fruits
     /home/ubuntu/hungry/fruits/valencia.qty
     /home/ubuntu/hungry/fruits/cavendish.qty
     /home/ubuntu/hungry/fruits/plantain.qty
     /home/ubuntu/hungry/fruits/asian.qty
     /home/ubuntu/hungry/fruits/empire_qc.qty
     /home/ubuntu/hungry/fruits/yellow_snow.qty
     /home/ubuntu/hungry/fruits/blood.jpg
     /home/ubuntu/hungry/fruits/cara_cara.jpg
     /home/ubuntu/hungry/fruits/red_banana.qty
     /home/ubuntu/hungry/fruits/clementine.qty
     /home/ubuntu/hungry/fruits/mandarins.jpg
     /home/ubuntu/hungry/fruits/clementines.jpg
     /home/ubuntu/hungry/fruits/bartlett.qty
     /home/ubuntu/hungry/fruits/granny_smith.jpg
     /home/ubuntu/hungry/fruits/mango.qty
     /home/ubuntu/hungry/fruits/empire.qty
     /home/ubuntu/hungry/fruits/granny_smith.qty
     /home/ubuntu/hungry/fruits/mandarin.qty
     /home/ubuntu/hungry/fruits/cortland.jpg
     /home/ubuntu/hungry/fruits/oranges
     /home/ubuntu/hungry/fruits/apples
     /home/ubuntu/hungry/fruits/cara_cara.qty
     /home/ubuntu/hungry/fruits/macinthosh_qc.qty
     /home/ubuntu/hungry/fruits/blood.qty
     /home/ubuntu/hungry/fruits/goldfinger.qty
     /home/ubuntu/hungry/fruits/red_delicious.qty
     /home/ubuntu/hungry/fruits/bananas
     /home/ubuntu/hungry/fruits/pisang_raja_indonesia.qty
     /home/ubuntu/hungry/fruits/navel.qty
     /home/ubuntu/hungry/fruits/pears
     ubuntu@flow:~/hungry$ 

Notes:

  * topics are server side, so they are applied first (order has no effect)

  * accept is processed apply client-side, and the first match wins.

  * Because of *mirror off* for the fruits, they are no longer in sub-directories like 
    oranges, pears, apples, bananas.


One can see that, while the fruits are all in the single fruit directory (because mirror off) the vegetables,
are still in multiple ones (mirror on.)
    

Uploading/Noticing
------------------

There are many different ways to create download messages to start files circulating in a Sarracenia
network.

   * sr3_cpost - post a file, or watch a directory (C-binary)
   * sr3_post - post a file (python script.)
   * sr3_watch - watch a directory (python)
   * sr3_poll - poll a remote directory or web resource. 
   * sr3 flow - for doing weird things.



userdir/sr_cpost
~~~~~~~~~~~~~~~~

So far, we have used sr3_cpost, a one-shot binary to post messages about file given on the
command line. One can also use the same binary as a service daemon to watch a directory by adding the *sleep* 
directive.

  ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3 edit cpost/my_feed** ::

    post_broker amqp://tsource@localhost
    post_exchange xs_tsource_public
    #post_baseUrl file:/

    # for later...
    #post_baseUrl file:${HOME}/sr3-examples/empty-amqp-pump/sample/groceries
    #
    sleep 5
    path ${HOME}/public_html
    post_baseUrl http://localhost/~${USER}
    post_baseDir ${HOME}/public_html

Now have:

  * added *sleep 5* which means it should sleep for at most 5 seconds before noticing a file.  
  * We moved the -p argument into the configuration file as the *path* and it is going to monitor the ${HOME}/feed directory.  
  * changed post_baseUrl to be appropriate for the new location.


  ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sr3 edit cpost/my_feed** 

    * comment out the old post_baseUrl
    * add new line: sleep 5
    * add new line: path ${HOME}/public_html
    * add new line: post_baseUrl http://localhost/~${USER}
    * add new line: post_baseDir ${HOME}/public_html

  ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sudo apt install apache2**

   * ensure apache is installed. (if not done before.)

  ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sudo a2enmod userdir** ::

     Enabling module userdir.
     To activate the new configuration, you need to run:
       systemctl restart apache2

  ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **sudo systemctl restart apache2**

     * activate userdir support in apache.

  ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **mkdir ~/public_html ~/web_hungry**

     * make a userdir for posting, 
     * make web_hungry for a downloading subscriber.

  ubuntu@flow2:~/sr3-examples/empty-amqp-pump$ **chmod +x ~ ~/public_html**

     * allow apache daemon read access to userdir ( aka ~/public_html )

  ubuntu@flow2:~/sr3-examples/empty-amqp-pump$  **sr3 start cpost/my_feed subscribe/web_hungry**

  ubuntu@flow2:~/sr3-examples/empty-amqp-pump$  **cd ~/public_html**
  
  ubuntu@flow2:~/sr3-examples/empty-amqp-pump$  **echo hello >1stFile**

  ubuntu@flow2:~/sr3-examples/empty-amqp-pump$  **echo bonjour >2ndFile**

  ubuntu@flow2:~/sr3-examples/empty-amqp-pump$  **echo hola >3rdFile**

  ubuntu@flow2:~/sr3-examples/empty-amqp-pump$  **echo GutenMorgen >4thFile**

  ubuntu@flow2:~/sr3-examples/empty-amqp-pump$  **ls ~/web_hungry** ::

    ubuntu@flow:~/.cache/sr3/log$ ls -al ~/web_hungry
    total 40
    drwxrwxr-x  2 ubuntu ubuntu 4096 May  9 15:57 .
    drwxr-x--x 12 ubuntu ubuntu 4096 May  9 15:33 ..
    -rw-rw-r--  1 ubuntu ubuntu    6 May  9 15:35 1stFile
    -rw-rw-r--  1 ubuntu ubuntu    8 May  9 15:35 2ndFile
    -rw-rw-r--  1 ubuntu ubuntu    5 May  9 15:35 3rdFile
    -rw-rw-r--  1 ubuntu ubuntu   12 May  9 15:35 4thFile
    ubuntu@flow:~/.cache/sr3/log$ 

We can see that the file was made available in ~/publc_html and was copied to ~/web_hungry.

Note that to watch directories:

   * sr3 watch is the python implementation of sr3_cpost, uses the same configuration files
     but provides added flexibility
   * The *force_polling* flag is needed on cluster file systems.
   * There are different methods available for different volumes of files:
     https://metpx.github.io/sarracenia/Explanation/DetectFileReady.html

Polling a Web Site
~~~~~~~~~~~~~~~~~~

Most sites are not Sarracenia enabled, meaning they don't produce messages for each file they
publish. To get messages created, so that subscribers can start downloading their files,
we can use sr_poll.

From sr3_102, we have content in /var/www/html/data.



* sr3_cpost

* watch
  * after_accept.

* flow/scheduled.

