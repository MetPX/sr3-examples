
Instructions
------------

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
  logReject on  

EOT
fi

# start all the flows.
sr3 start

# check the status:
healthy status of running configuration::
    
    ubuntu@pump:/var/www/html/data$ sr3 status
    status: 
    Component/Config                         Processes   Connection        Lag                              Rates                                        
                                             State   Run Retry  msg data   Queued   LagMax  LagAvg  %rej     pubsub   messages     RxData     TxData 
                                             -----   --- -----  --- ----   ------   ------  ------  ----   --------       ----     ------     ------ 
    sarra/hpfx_mirror_alerts                 run     5/5     0 100%   0%      0    0.00s    0.00s  0.0%  0 Bytes/s   0 msgs/s  0 Bytes/s  0 Bytes/s
    sarra/hpfx_mirror_bulletins              run     5/5     0 100%   0%      0   44.57s    8.40s  0.0%  2.2 KiB/s   3 msgs/s 951 Bytes/s  0 Bytes/s
    sarra/hpfx_mirror_citypage_weather       run     5/5     0 100%   0%      1   53.14s   10.15s  2.6%  1.1 KiB/s   2 msgs/s 183.5 KiB/s  0 Bytes/s
    sarra/hpfx_mirror_hydrometric            run     5/5     0 100%   0%      0   45.69s   12.36s  0.0%  1.0 KiB/s   1 msgs/s 105.4 KiB/s  0 Bytes/s
    sarra/hpfx_mirror_lightning              run     5/5     0 100%   0%      0    0.00s    0.00s  0.0%  0 Bytes/s   0 msgs/s  0 Bytes/s  0 Bytes/s
    sarra/hpfx_mirror_marine                 run     5/5     0 100%   0%      0   16.43s    5.32s 26.4% 816 Bytes/s   1 msgs/s 22.0 KiB/s  0 Bytes/s
    sarra/hpfx_mirror_models                 run     5/5     0 100%   0%    106    5.21s    3.10s  0.0% 188 Bytes/s   0 msgs/s  3.3 MiB/s  0 Bytes/s
    sarra/hpfx_mirror_observations           run     5/5     0 100%   0%      6   45.56s    7.94s  3.3%  3.9 KiB/s   5 msgs/s 69.7 KiB/s  0 Bytes/s
    sarra/hpfx_mirror_other                  run     5/5     0 100%   0%      0    0.00s    0.00s  0.0%  0 Bytes/s   0 msgs/s  0 Bytes/s  0 Bytes/s
    sarra/hpfx_mirror_radar                  run     5/5     0 100%   0%      0   16.41s    5.24s 20.5% 861 Bytes/s   1 msgs/s 24.2 KiB/s  0 Bytes/s
    sarra/hpfx_mirror_satellite              run     5/5     0 100%   0%      0    0.00s    0.00s  0.0%  0 Bytes/s   0 msgs/s  0 Bytes/s  0 Bytes/s
          Total Running Configs:  11 ( Processes: 55 missing: 0 stray: 0 )
                         Memory: uss:1.7 GiB rss:2.5 GiB vms:3.9 GiB 
                       CPU Time: User:67.98s System:19.55s 
    	   Pub/Sub Received: 16 msgs/s (10.0 KiB/s), Sent:  14 msgs/s (7.9 KiB/s) Queued: 113 Retry: 0, Mean lag: 8.03s
    	      Data Received: 14 Files/s (3.7 MiB/s), Sent: 0 Files/s (0 Bytes/s) 
    ubuntu@pump:/var/www/html/data$ 
    
Observations
------------

* you can see the average lag is a few seconds.
* there will often be outliers in lag: a few that get delivered slowly.
* the feeds are separated by data type. so that weather warnings (very high priority) are not waiting for model data (usually longer time span) to arrive.
* the *hpfx_mirror_models* configuration has a queue, because the data is very large, and so the acquisition will naturally see delays. Again, we don't want delays in model data aquisition to slow down smaller more punctually important data.
* All of these mirrors are using 5 instances, (not yet tuned) likely most of them can be tuned downward to reflect the needs of realistic data flow rates.

Omissions
---------

# No SSL... add here...
# SSL for apache...
# SSL for rabbitmq.

 #./add_mosquitto.sh - to add mqtt publishing support
 # no SSL for mosquitto
