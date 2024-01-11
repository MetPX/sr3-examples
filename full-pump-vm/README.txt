


Given an empty Ubuntu 22.04 (or later) ( such as created by: multipass launch -m 8G -d 30G --name pump )

run the script here:

 sudo apt update

 sudo apt upgrade

 git clone https://github.com/MetPX/sr3-examples/

 cd sr3-examples/empty-amqp-pump

 ./rabbitmq_pump_setup.sh
 ./add_apache_httpd.sh



# Add sr3 configurations to download and republish.

    cd config/sr3
    for d in *; do
       mkdir -p ~/.config/sr3/$d
    done
    for cfg in */*; do
       cp ${cfg} ~/.config/sr3/${cfg}
       echo copied ${cfg}
    done

# sr3 status


# better to publish with v03:

if [ ! "`grep post_TopicPrefix ~/.config/sr3/default.conf`" ]; then
  cat >>~/.config/sr3/default.conf  <<EOT  

  post_topicPrefix v03.post
  post_format v03
  
EOT
fi

# start all the flows.
sr3 start

# No SSL... add here...
# SSL for apache...
# SSL for rabbitmq.

 #./add_mosquitto.sh - to add mqtt publishing support
 # no SSL for mosquitto
