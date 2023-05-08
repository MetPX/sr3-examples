
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

In this message the relative path (from the "relPath" field) is "grains/bread/whole_wheat" ...  
 
* Topic will be: v03.post.grains.bread
* whole_wheat is the file name


the subscriber has no information about the topic in it. but the default topicPrefix is v03.post,
and the default subtopic is #.  # is a wildcard to any combination of topics, so the main binding
which can bee seen in the rabbitmq display is to:

   xs_tsource_public  v03.post.#

which essentially means every file posted by sr3_cpost. (> 80 of them.)


Using subtopic
~~~~~~~~~~~~~~

Topic filtering reduces the number of unwanted messages downloaded by a client
for Example:

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

will then download only the fruits directory from the all the directories posted by cpost.
followed by:

   ubuntu@flow2:~/sr3-examples/empty-amqp-pump$  **cd ~/hungry**

   ubuntu@flow2:~/hungry$ **find `pwd`**

::

    /home/ubuntu/hungry
    /home/ubuntu/hungry/fruits
    /home/ubuntu/hungry/fruits/mango
    /home/ubuntu/hungry/fruits/oranges
    /home/ubuntu/hungry/fruits/oranges/blood
    /home/ubuntu/hungry/fruits/oranges/mandarin
    /home/ubuntu/hungry/fruits/oranges/clementine
    /home/ubuntu/hungry/fruits/oranges/navel
    /home/ubuntu/hungry/fruits/oranges/cara_cara
    /home/ubuntu/hungry/fruits/oranges/valencia
    /home/ubuntu/hungry/fruits/apples
    /home/ubuntu/hungry/fruits/apples/macintosh_qc
    /home/ubuntu/hungry/fruits/apples/empire_qc
    /home/ubuntu/hungry/fruits/apples/empire
    /home/ubuntu/hungry/fruits/apples/red_relicious
    /home/ubuntu/hungry/fruits/apples/granny_smith
    /home/ubuntu/hungry/fruits/bananas
    /home/ubuntu/hungry/fruits/bananas/red_banana
    /home/ubuntu/hungry/fruits/bananas/cavendish
    /home/ubuntu/hungry/fruits/bananas/pisang_raja_indonesia
    /home/ubuntu/hungry/fruits/bananas/plantain
    /home/ubuntu/hungry/fruits/bananas/goldfinger
    /home/ubuntu/hungry/fruits/pears
    /home/ubuntu/hungry/fruits/pears/asian
    /home/ubuntu/hungry/fruits/pears/yellow_snow
    /home/ubuntu/hungry/fruits/pears/bartlett
    ubuntu@flow2:~/hungry$ 


    
* Where messages come from
  * broker
  * exchange.
* Message Structure.
* Topics
* paths
* accept/reject
* after_accept

Uploading/Noticing:

* sr3_cpost
   * sleep > 0

* watch
  * after_accept.

* poll

* flow

* flow/scheduled.

