


# To test the uplink

The purpose is to provide a continuous feed for testing/demonstration purposes.

## get a constant flow of files.

list some examples of flow config files available:

```

bob@loli:~/.cache/sr3/log$ sr3 list ie
Sample Configurations: (from: /home/bob/.local/lib/python3.10/site-packages/sarracenia/examples )
cpump/cno_trouble_f00.inc        flow/amserver.conf               flow/bc_trans.conf               flow/opg.conf
flow/poll.inc                    flow/post.inc                    flow/report.inc                  flow/sarra.inc
flow/scheduled_aviation_wind_fax_charts.conf flow/sender.inc                  flow/shovel.inc                  flow/subscribe.inc
flow/watch.inc                   flow/winnow.inc                  poll/airnow.conf                 poll/aws-nexrad.conf
poll/copernicus_odata.conf       poll/mail.conf                   poll/nasa-mls-nrt.conf           poll/nasa_cmr_opendap.conf
poll/nasa_cmr_other.conf         poll/nasa_cmr_podaac.conf        poll/noaa.conf                   poll/soapshc.conf
poll/usgs.conf                   post/WMO_mesh_post.conf          sarra/bc_trans.conf              sarra/wmo_mesh.conf
sender/am_send.conf              sender/ec2collab.conf            sender/pitcher_push.conf         shovel/no_trouble_f00.inc
subscribe/aws-nexrad.conf        subscribe/dd_2mqtt.conf          subscribe/dd_all.conf            subscribe/dd_amis.conf
subscribe/dd_aqhi.conf           subscribe/dd_cacn_bulletins.conf subscribe/dd_citypage.conf       subscribe/dd_cmml.conf
subscribe/dd_gdps.conf           subscribe/dd_radar.conf          subscribe/dd_rdps.conf           subscribe/dd_swob.conf
subscribe/ddc_cap-xml.conf       subscribe/ddc_normal.conf        subscribe/download_all_nasa_earthdata.conf subscribe/downloademail.conf
subscribe/ec_ninjo-a.conf        subscribe/get_copernicus.conf    subscribe/hpfxWIS2DownloadAll.conf subscribe/hpfx_amis.conf
subscribe/hpfx_citypage.conf     subscribe/local_sub.conf         subscribe/ping.conf              subscribe/pitcher_pull.conf
subscribe/sci2ec.conf            subscribe/subnoaa.conf           subscribe/subsoapshc.conf        subscribe/subusgs.conf
watch/master.conf                watch/pitcher_client.conf        watch/pitcher_server.conf        watch/sci2ec.conf
bob@loli:~/.cache/sr3/log$

```
lets get a feed of RADAR images:

```
bob@loli:~/.cache/sr3/log$  sr3 add subscribe/dd_radar.conf

bob@loli:~/.cache/sr3/log$  sr3 edit subscribe/dd_radar.conf
# adjust directory to be ${HOME}/to_hpfx/dd_radar
# subtopic:
# the example only gets one RADAR: XAM (which I think doesn't exist anymore.)
# to get all the RADARS, change XAM to *
# adjust subtopic to be ${HOME}/to_hpfx/dd_radar
# subtopic should be: *.WXO-DD.radar.CAPPI.GIF.*.#
bob@loli:~/.cache/sr3/log$  sr3 start subscribe/dd_radar.conf

```

Now you have a constant flow of GIF images of RADAR data from all across the country 
downloaded into ~/to_hpfx/dd_radar

The images are noticed by the *sr3 watch* daemon, published for the *sr3 sender*
and thus uploaded to hpfx.

# Check & Delete on Hpfx.

HPFX server already has metpx-sr3 installed system-wide, so can just use the default one.

This sr3 client will:
* subscribe to the incoming radar image feed.
* check if the current product is the next one after the previous one.
  * emit an ERROR missing file message if that is the case.
* delete the file after between 5 and 10 minutes (if uptodate... if far behind might 
  delete right away...)

```
mkdir -p ~/.config/sr3/subscribe
cat >~/.config/sr3/subscribe/del_rad.conf <<EOT

broker amqps://pas037@hpfx.collab.science.gc.ca

exchange xs_pas037_new_in_to_hpfx

# change url from SFTP to file:
baseDir ${HOME}/on_hpfx
callback sarracenia.flowcb.accept.tolocalfile.ToLocalFile

# check if the radar file is the one we expected (valid date/time in filename)
callback every_rad

# wait at least 30 seconds after delivery.
# if it's not old enough, it gets queued for retry after 5 minutes.
fdelay 30
callback filter.fdelay

# after the delay, delete the file... I'm done with it.
delete_source on

# on average, there should be one or two passes of radar data from the country
# in the dd_radar folder.


# We are just processing messages, not copying the data itself.
# to avoid *download no*, could us a "shovel" instead of a "subscribe" component.
# In a shovel, that is the default.
download no

# only interested in the dd_radar directory/topic.

subtopic dd_radar

accept .*
EOT


```


# Set up sr3 client on hpfx (remote cluster server.)

Now need something to clean up the images once they get to hpfx (to avoid space exhaustion.)
Setup metpx-sr3 on hpfx.collab.science.gc.ca. Well the package already installed.

Check if you need to need to set up daemon to run constantly:

```

pas037@hpfx3:~$ crontab -l
9,18,36,45,54 * * * * VIP='142.98.224.27';RESULT=`/sbin/ip addr show | grep $VIP|wc|awk '{print $1}'`; if [ $RESULT -eq 1 ]; then /usr/bin/sr3 sanity ; fi  >> ${HOME}/.cache/sr3/log/cron_sanity.log  2>&1
pas037@hpfx3:~$

```

OK check for user level systemd unit:
```

pas037@hpfx3:~/.cache/sr3/log$ systemctl --user status metpx-sr3_user
Unit metpx-sr3_user.service could not be found.
pas037@hpfx3:~/.cache/sr3/log$


```

install and activate the unit file as was done on loli:

```

   mkdir -p ~/.config/systemd/user
   cd ~/.config/systemd/user
   wget https://raw.githubusercontent.com/MetPX/sarracenia/refs/heads/stable/tools/metpx-sr3_user.service
   #or if sr3 > 3.0.56: wget https://raw.githubusercontent.com/MetPX/sarracenia/refs/heads/development/tools/metpx-sr3_user.service

   # edit as required...
```

NOTE: until 3.0.57 is released, replace *stable* by *development* in url above, the stable one does not work properly.

now that the service file is there, can activate it:

```
pas037@hpfx3:~/.config/systemd/user$ systemctl --user enable metpx-sr3_user
Created symlink /home/pas037/.config/systemd/user/default.target.wants/metpx-sr3_user.service → /home/pas037/.config/systemd/user/metpx-sr3_user.service.
pas037@hpfx3:~/.config/systemd/user$ 

```

then start it up using systemctl

```

pas037@hpfx3:~/.config/systemd/user$ systemctl --user status metpx-sr3_user
● metpx-sr3_user.service - Sarracenia V3 File Copy Service
     Loaded: loaded (/home/pas037/.config/systemd/user/metpx-sr3_user.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2024-12-12 16:03:38 UTC; 16s ago
   Main PID: 680289 (python3)
      Tasks: 1 (limit: 230331)
     Memory: 29.9M
        CPU: 3.271s
     CGroup: /user.slice/user-66017.slice/user@66017.service/app.slice/metpx-sr3_user.service
             └─680289 /usr/bin/python3 /usr/lib/python3/dist-packages/sarracenia/instance.py --no 1 start subscribe/del_rad

Dec 12 16:03:35 hpfx3 systemd[2538760]: Starting Sarracenia V3 File Copy Service...
Dec 12 16:03:38 hpfx3 sr3[678306]: starting:.( 1 ) Done
Dec 12 16:03:38 hpfx3 systemd[2538760]: Started Sarracenia V3 File Copy Service.
pas037@hpfx3:~/.config/systemd/user$ sr3 status
status:
Component/Config     Processes   Connection        Lag                              Rates
                     State   Run Retry  msg data   Que   LagMax   LagAvg Last  %rej     pubsub   messages     RxData     TxData
                     -----   --- -----  --- ----   ---   ------   ------ ----  ----     ------   --------     ------     ------
subscribe/del_rad    idle    1/1   116 100%   0%     0    0.00s    0.00s  n/a  0.0%       0B/s       0m/s       0B/s       0B/s
      Total Running Configs:   1 ( Processes: 1 missing: 0 stray: 0 )
                     Memory: uss:29.3MiB rss:41.6MiB vms:55.5MiB
                   CPU Time: User:0.42s System:0.04s
           Pub/Sub Received: 0m/s (0B/s), Sent:  0m/s (0B/s) Queued: 0 Retry: 116, Mean lag: 0.00s
              Data Received: 0f/s (0B/s), Sent: 0f/s (0B/s)
pas037@hpfx3:~/.config/systemd/user$

```

Note: if restarted using sr3 (sr3 stop or sr3 restart) systemctl will lose track.
use sr3 status to monitor. Startup will still occur on next system startup.


