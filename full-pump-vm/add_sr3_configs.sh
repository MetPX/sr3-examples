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
logReject on  

EOT
fi
