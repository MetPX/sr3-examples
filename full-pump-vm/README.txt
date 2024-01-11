
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
 ./add_sr3_configs.sh

crontab -e 
17 * * * * `pwd`/web_cleanup.sh

# start all the flows.
sr3 start

It takes a few minutes to start up, if invoking sr3 status while startup is in progress, will see
messages about stray processes. Once startup is complete, output should be clean.
 
# check the status:
healthy status of running configuration::
             
    ubuntu@pump:~/.cache/sr3/log$ sr3 status
    status: 
    Component/Config                         Processes   Connection        Lag                              Rates                                        
                                             State   Run Retry  msg data   Queued   LagMax  LagAvg  %rej     pubsub   messages     RxData     TxData 
                                             -----   --- -----  --- ----   ------   ------  ------  ----   --------       ----     ------     ------ 
    sarra/hpfx_mirror_alerts                 run     2/2     0 100%   0%      0    0.00s    0.00s  0.0%  0 Bytes/s   0 msgs/s  0 Bytes/s  0 Bytes/s
    sarra/hpfx_mirror_bulletins              run     5/5     0 100%   0%      3    8.17s    1.98s  0.0%  1.4 KiB/s   1 msgs/s  1.3 KiB/s  0 Bytes/s
    sarra/hpfx_mirror_citypage_weather       run     5/5     0 100%   0%      0   10.25s    5.35s  0.0% 78 Bytes/s   0 msgs/s  5.4 KiB/s  0 Bytes/s
    sarra/hpfx_mirror_hydrometric            run     1/1     0 100%   0%      0    2.02s    0.73s  2.2%  2.0 KiB/s   2 msgs/s 101.7 KiB/s  0 Bytes/s
    sarra/hpfx_mirror_lightning              run     2/2     0 100%   0%      0    0.00s    0.00s  0.0%  0 Bytes/s   0 msgs/s  0 Bytes/s  0 Bytes/s
    sarra/hpfx_mirror_marine                 run     2/2    20 100%   0%      0  320.30s   28.44s 46.3% 715 Bytes/s   2 msgs/s 18.0 KiB/s  0 Bytes/s
    sarra/hpfx_mirror_models                 run     5/5     0 100%   0%      0    0.00s    0.00s  0.0%  0 Bytes/s   0 msgs/s  0 Bytes/s  0 Bytes/s
    sarra/hpfx_mirror_observations           run     8/8     0 100%   0%      0    9.61s    3.01s  9.4%  3.9 KiB/s   5 msgs/s 80.2 KiB/s  0 Bytes/s
    sarra/hpfx_mirror_other                  run     5/5     0 100%   0%      0    8.42s    6.56s  2.8% 161 Bytes/s   0 msgs/s  1.7 KiB/s  0 Bytes/s
    sarra/hpfx_mirror_radar                  run     5/5    20 100%   0%      0  327.01s   28.15s  9.0%  1.0 KiB/s   2 msgs/s 34.2 KiB/s  0 Bytes/s
    sarra/hpfx_mirror_satellite              run     5/5     0 100%   0%      0    6.81s    6.55s  0.0% 10 Bytes/s   0 msgs/s 272.9 KiB/s  0 Bytes/s
          Total Running Configs:  11 ( Processes: 45 missing: 0 stray: 0 )
                         Memory: uss:1.4 GiB rss:2.1 GiB vms:3.2 GiB 
                       CPU Time: User:49.31s System:8.09s 
    	   Pub/Sub Received: 15 msgs/s (9.3 KiB/s), Sent:  13 msgs/s (7.2 KiB/s) Queued: 3 Retry: 40, Mean lag: 9.72s
    	      Data Received: 13 Files/s (515.5 KiB/s), Sent: 0 Files/s (0 Bytes/s) 
    ubuntu@pump:~/.cache/sr3/log$ 
    
    
    
Observations
------------

* you can see the average lag is a few seconds.
* there will often be outliers in lag: a few items in a flow that get delivered slowly, as shown in LagMax.
* the feeds are separated by data type. so that weather warnings (very high priority) are not waiting for model data (usually longer time span) to arrive.
* the *hpfx_mirror_models* configuration has a queue, because the data is very large, and so the acquisition will naturally see delays. Again, we don't want delays in model data aquisition to slow down smaller more punctually important data.
* In the Run column, the denominator is the number of instances (or processes) configured to run.  the numerator is the number actually running.
  This display is healthy. Different configurations have different numbers of instances configured to reflect the data volumes and download priority.
  This is manually tuned by administrators.
* %rej numbers, the configurations are such that there are no reject statements in the configurations. So any rejection is interesting.
  looking athe logs we see messages:

  * sarra_hpfx_mirror_other_01.log:2024-01-11 13:29:29,116 [INFO] sarracenia.flowcb.log after_work rejected: 304 same checksum /var/www/html/data/20240111/WXO-DD/marine_weather/xml/pacific/m0000106_f.xml  
  * sarra_hpfx_mirror_radar_03.log:2024-01-11 13:30:44,998 [INFO] sarracenia.flowcb.log after_work rejected: 304 mtime not newer /var/www/html/data/20240111/WXO-DD/radar/PRECIPET/GIF/CASSU/202401111830_CASSU_PRECIPET_RAIN.gif  

  and that is all. So the rejections are legitimate duplicate suppression.

  

Omissions
---------

# No SSL... add here...
# SSL for apache...
# SSL for rabbitmq.

 #./add_mosquitto.sh - to add mqtt publishing support
 # no SSL for mosquitto
