
# Hot Directory to Upload Files to a Cluster  

**Presume:**

* we have someone handy with linux command line.
* we have a local linux server, with access to large data sets 
* we have a cluster (called gpsc), or data centre with a lot of storage.
* ssh access between local and remote.
* we want to upload data from the local linux server to the remote data centre.
* the normal linux way to have a long running service is to run processes in
  the background (called a *daemon* in linux/unix.)


**What we are doing:**

* install metpx-sr3 toolkit, which has code for some daemons.
* configure and run 1 daemon that watches a directory we pick on the local server.
* configure and run n daemons that send the files watch found to the cluster.
* once the n+1 daemons are configured to run:
  * if you put a file in the local directory, it will get copied to remote.

* the daemons should be restart automatically when the system is restarted.
* if any daemons crash, they should be restarted automatically.
* any transfers queued should be picked up where they left off.

* it is reasonably performant, but not exceptional, but it's kind of a turtle/hare story:
  * individual file transfer not particularly tuned. Make it up in volume.
  * run always, robust restart/continuation.
  * for small files amortize connections by sending multiple files with one connection.
  * for large files, use binary accellerators.
  * run multiple transfers at once in parallel (to overcome/mitigate tcp failings for single transfers.)
  * if some special tuning is desired, transfer methods are configurable.



## Need:

* local linux server: call it *loli*

   * an account with access to the files to be copied. 
   * the sarracenia clients installed:
     * metpx-sr3 python toolkit.
   * we'll call the local user: bob
   * there is a directory here ~bob/to_hpfx


* remote cluster server, called *hpfx*
   * an account on the remote server.  (say pas037)
   * a directory with enough room to put the data. (say ~pas037/on_hpfx)
   * an account on the rabbitmq (amqp) broker on the cluster. (say: pas037)
   * call the server hpfx.collab.science.gc.ca (call it hpfx for short.)
     hpfx.collab.science.gc.ca has access to the cluster's storage.

supporting materials provided:

* the config files built here are also present in the subdirectories
  in the same tree as this file. One can copy from the tree,
  of copy/paste content from this document.

     * *loli_config/* subdirectory would be *~/.config* in a user account on the local linux server.
     * *loli_config/ssh* would be the *~/.ssh* directory in a user account.
     * *hpfx_config/* files file which would be in *~/.config* on hpfx (barely used.) 
     * *hpfx_config/ssh* what needs to be on remote ~/.ssh to acccept client key.

  After copying the files, one perform global substitutions 
  with: find hpfx_config/ -type f | xargs sed -i 's+pas037+good001+g'  

* Documentation on metpx-sr3:  https://metpx.github.io/sarracenia

 
## Sample metpx-sr3 installation method.

This section assumes installing a Python package via pip in a user account.
Better system integration is provided on ubuntu via debian packages.
RPM packages are also available for redhat.  This procedure will work
regardless of distribution, and without administrative access to loli
or hpfx.

* add ~/.local/bin to PATH.

```shell

vi ~/.bash_profile 
insert:
# set PATH so it includes user's private bin if it exists
for d in  ~/.local/bin ~/bin ; do
    if [ -d $d ] ; then
        PATH=${d}:"${PATH}"
    fi
done

```

```shell
pip3 install --user metpx-sr3

```

* logout and log in again to get ~/.local/bin added to PATH

```shell

bob@loli:~$ sr3 features 2>/dev/null

Status:    feature:   python imports:      Description:
Installed  amqp       amqp                 can connect to rabbitmq brokers
Absent     azurestorage azure-storage-blob   cannot connect natively to Azure Stoarge accounts
Installed  appdirs    appdirs              place configuration and state files appropriately for platform (windows/mac/linux)
Installed  filetypes  magic                able to set content headers
Absent     ftppoll    dateparser,pytz      not able to poll with ftp
Installed  humanize   humanize,humanfriendly humans numbers that are easier to read.
Absent     jsonlogs   pythonjsonlogger     only have raw text logs
Absent     mqtt       paho.mqtt.client     cannot connect to mqtt brokers (need >= 2.1.0)
Installed  process    psutil               can monitor, start, stop processes:  Sr3 CLI should basically work
MISSING    reassembly flufl.lock           need to lock block segmented files to put them back together
Absent     redis      redis,redis_lock     cannot use redis implementations of retry and nodupe
Installed  retry      jsonpickle           can write messages to local queues to retry failed publishes/sends/downloads
Absent     s3         boto3                cannot connect natively to S3-compatible locations (AWS S3, Minio, etc..)
Installed  sftp       paramiko             can use sftp or ssh based services
Installed  vip        netifaces            able to use the vip option for high availability clustering
Installed  watch      watchdog             watch directories
Installed  xattr      xattr                will store file metadata in extended attributes

 state dir: /home/bob/.cache/sr3
 config dir: /home/bob/.config/sr3

bob@loli:~$

```

First column features says whether a given feature is enabled in the current installation.
if some needed feature is *Absent* then one needs to install the python packages listed
in the third column. (they can be OS packages, or via pip/pip3)

for example:

```shell

  pip3 install --user amqp appdirs humanize humanfriendly netifaces psutil paramiko watchdog xattr 

```

* if systemd is available, get user mode service file

```shell

   bob@loli:~$ mkdir -p ~/.config/systemd/user
   bob@loli:~$ cd ~/.config/systemd/user

   # currently:
   bob@loli:~$ wget https://raw.githubusercontent.com/MetPX/sarracenia/refs/heads/development/tools/metpx-sr3_user.service

   # OR, after 3.0.57 is released:
   bob@loli:~$ wget https://raw.githubusercontent.com/MetPX/sarracenia/refs/heads/stable/tools/metpx-sr3_user.service

   bob@loli:~$ vi metpx-sr3_user.service
   # replace /usr/bin/sr3 by where it really is: /home/bob/.local/bin/sr3
   # in vi something like below would do that:
   :%s+/usr/bin/sr3+/home/bob/.local/bin/sr3+

   # so it starts up with the server in this account.
   bob@loli:~$ loginctl enable-linger
   bob@loli:~$ systemctl --user enable metpx-sr3_user

```

* if systemd is unavailable... need something else to start it.
  (not covered for now.) something to invoke *sr3 start|stop* when needed.

* given that sr3 has been started, there is an auditor process to restart 
  processes that may have crashed (sr3 sanity)

* if loli is part of an HA cluster with a VIP, then only want sarracenia
  running on the node with the vip:

```shell

bob@loli:~$ crontab -l
9,18,36,45,54 * * * * VIP='192.168.46.173';RESULT=`/sbin/ip addr show | grep $VIP|wc|awk '{print $1}'`; if [ $RESULT -eq 1 ]; then ${HOME}/.local/bin/sr3 sanity ; fi  >> ${HOME}/.cache/sr3/log/cron_sanity.log  2>&1
bob@loli:~$

```

In the case of vip usage, one likely needs a similar setting in the config files
```

vip 192.168.46.173

```
So that if sr3 is started on the passive node, it realizes and goes into passive
mode. On the other hand, if you don't have an HA vip setup, then 
the following cron job is sufficient:

```shell

9,18,36,45,54 * * * * ${HOME}/.local/bin/sr3 sanity >> ${HOME}/.cache/sr3/log/cron_sanity.log  2>&1

```

the processes do not crash very often, so a large proportion of the time, this
cron job will do nothing. Sample output:

```shell
   
bob@loli:~/.cache/sr3/log$ tail sanity.log

sanity: 2024-12-11 12:54:02,072 929959 [INFO] sarracenia.flow.watch __init__ watching!
no missing processes found
no stray processes found

sanity: 2024-12-11 13:09:01,242 930804 [INFO] sarracenia.flow.watch __init__ watching!
no missing processes found
no stray processes found

bob@loli:~/.cache/sr3/log$

```


## Setup SSH for Passwordless Access.

The tool will be doing transfers in the background using ssh protocols. 
One must be able to ssh into the remote server from the local one 
without a prompt (password or otherwise.) It needs to be able to 
non-interactively log into the remote server. Nothing special, 
just picking the current key algo recommendations,
but anything is compliant with security recommendations is fine.
(this is from 2024/12, recommendations change often.)
Example:


```shell

bob@loli:~$ ssh-keygen -t ed25519 -f ~/.ssh/loli_bob_ed25519
Generating public/private ed25519 key pair.
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /home/bob/.ssh/loli_bob_ed25519
Your public key has been saved in /home/bob/.ssh/loli_bob_ed25519.pub
The key fingerprint is:
SHA256:9F73kkDrJJhb0yoq/pwxDWyHW4EGYe7a/k4O3xVA/GA bob@loli
The key's randomart image is:
+--[ED25519 256]--+
|    +. ..        |
|   o . oE        |
|    . o.+o  .    |
|   . o o *.o .   |
|    . = S * * .  |
|   o . * + O o o |
|  . o = + + . o .|
|   ..* * o     . |
|   .o=X .        |
+----[SHA256]-----+
bob@loli:~$ 
bob@loli:~/.ssh$ scp loli_bob_ed25519.pub pas037@hpfx.collab.science.gc.ca:.ssh
pas037@hpfx.collab.science.gc.ca's password:
loli_bob_ed25519.pub                              100%  100     2.7KB/s   00:00
bob@loli:~/.ssh$ssh pas037@hpfx.collab.science.gc.ca
pas037@hpfx:~/$ cd ~/.ssh
pas037@hpfx:~/.ssh$ cat loli_bob_ed25519.pub >>authorized_keys
pas037@hpfx:~/$ chmod 600 authorized_keys

```

* configure bob@loli's ~/.ssh/config to use the right info:

```

Host hpfx
Hostname hpfx.collab.science.gc.ca
User pas037
IdentityFile ~/.ssh/loli_bob_ed25519

```

* install public key on hpfx (in ~/.ssh/authorized_keys (done above with scp.)
* ssh in once interactively to accept the host key.


so now logins without a password should work, e.g.:

```shell

bob@loli:~/.ssh$ ssh hpfx uname -a
Linux hpfx3 6.8.0-48-generic #48~22.04.1-Ubuntu SMP PREEMPT_DYNAMIC Mon Oct  7 11:24:13 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
bob@loli:~/.ssh$

```
   

## Setup an AMQP Publisher for bob@loli


```shell

bob@loli:~$ mkdir -p ~/to_hpfx  # local uplink directory for files destined for hpfx.
bob@loli:~$ mkdir -p ~/.config/sr3/watch

bob@loli:~$ ssh hpfx.collab.science.gc.ca -c 'mkdir -p ~/on_hpfx' # directory to store files in.

```

Note that to_hpfx needs to be in a file system with enough space to hold all 
the files expected to transit through it.

Cleanup of this directory after transfer is complete is outside the 
scope of this exercise.

### write the amqp auth information to a local credential store:

    echo amqps://pas037:pas037_password@hpfx.collab.science.gc.ca >>~/.config/sr3/credentials.conf


### create a directory watcher.

```shell 

bob@loli:-$ cat >~/.config/sr3/watch/to_hpfx.conf <<EOT

post_broker amqps://pas037@hpfx.collab.science.gc.ca
post_exchange xs_pas037_loli_bob_to_hpfx

post_baseUrl file:${HOME}/to_hpfx
path ${HOME}/to_hpfx

nodupe_ttl on

# exclude working files (that end in .tmp)
reject .*.tmp$
accept .*

EOT

bob@loli:-$  sr3 declare

```

*sr3 declare* should connect to the broker and declare the exchange the watch
will be posting to. If the declare does not succeed, stop here
and debug until it does.



### Create a Sender

```shell

mkdir -p ~/.config/sr3/sender

cat >~/.config/sr3/sender/to_hpfx.conf <<EOT

broker amqps://pas037@hpfx.collab.science.gc.ca
exchange xs_pas037_loli_bob_to_hpfx

# sento host should match Host in ~/.ssh/config
sendTo sftp://hpfx

# how many parallel transfer processes.
instances 5 

# by default file removals will also be updated on hpfx.
#fileEvents -delete,rmdir

# use scp binary for files bigger than a threshold.
# for smaller files, it batches a whole batch of transfers over a single
# connection, saving setup/teardown per file, but done in python.
# for larger files, a binary will consume less cpu, and likely be faster
# if the link between both ends can support it.
accelThreshold 1M

# perhaps you have a faster/better large file transfer method available?
# wrap it in a script that accepts scp style invocation
# accelScpCommand /usr/bin/your_fancy_scp %s %d


# while files are being uploaded, have a .tmp suffix:
inflight .tmp

nodupe_ttl on

# exclude working files (that end in .tmp)
reject .*.tmp$
accept .*

post_broker hpfx://pas037@hpfx.collab.science.gc.ca

post_baseUrl sftp://pas037@hpfx.collab.science.gc.ca/on_hpfx

# make the posted path relative to this:
post_baseDir /home/pas037/on_hpfx

post_exchange xs_pas037_on_hpfx

EOT

```

### Start it up.


```shell

bob@loli:~$ systemctl --user start metpx-sr3_user
bob@loli:~$ sr3 status
bob@loli:~$ sr3 status
status:
Component/Config     Processes   Connection        Lag                              Rates
                     State   Run Retry  msg data   Que   LagMax   LagAvg  Last  %rej     pubsub   messages     RxData     TxData
                     -----   --- -----  --- ----   ---   ------   ------  ----  ----     ------   --------     ------     ------
sender/to_hpfx       idle    5/5     0 100%   0%     0   23.27s   11.17s 3m28s 21.3%     206B/s       0m/s       0B/s       0B/s
watch/to_hpfx        idle    1/1     0 100%   0%     0    0.00s    0.00s   n/a  0.0%       0B/s       0m/s       0B/s       0B/s

```

* note that to monitor sr3, it is better to use *sr3 status*...
  it is a known issue that systemd will claim it is down, when it is 
  fine. to start/stop, use systemctl, but to see status use sr3 cli.
  although sr3 restart is fine also. The purpose of systemd integration
  is for ensuring sr3 is started when the system boots.

It should be running now.


## Faster?

Often, a single tcp stream cannot make effective use of the bandwidth available between
two points, especially when latency is large. The simplest and often most effective 
means of increasing bandwidth utilisation, given a sufficient volume of files to 
transfer, is to have more instances participating in the transfer:

```

instances 10


```

So now, after *sr3 restart sender/to_hpfx*, it will run 10 processes transferring
files. One can increase instance upto around 40 or so in a single configuration.
After that point, it is generally better to split into multiple configurations.

The small file transfers are probably as fast as they are going to get, so the large files are
more likely the issue. Metpx-sr3 has binary accelleration invocation built in and
tunable. The accelScpCommand can be used to change the binary (or flags to the 
binary, e.g. for buffer sizes.) 

```

accelScp /usr/bin/scp -B -s -l 1024 %s %d

```

these switches are:

* -B ... no interactive prompts ( -B )
* -s use SFTP protocol (instead of earlier scp one.)
* -l limit bandwidth to the given number of KB/sec.

The %s and %d options are replaced by the source and destination specifications
in a format accepts by the standard scp command. One can use options such 
as *ConnectMaster* to have longer lasting binary connections.
One can replace /usr/bin/scp by some other program, or give it the -S flag to replace
just the encrypted transport.


## Try it out

So it should be working now. the installation is complete.

* copy files in the directory... see how they show up on the other side.
* copy trees into the directory... see how the multiple instances provide parallellism.
* reboot the server, see that the daemons recover and continue.
* kill some instances... see that sanity restarts them.
* kill the networking... see that when the networking returns... it is patient... recovers and continues.
  * caveat... if the server is rebooted while the network is down... have to look...
* add subscriptions gpsc (a second cluster) to pull files from hpfx (copying from 1 network zone to a second one.)
* if a file is missed... should likely describe how to recover... 
  * use touch.
* if a file foobar is only half-way there...
  * it will be named foobar.tmp on hpfx.
  * hpfx will only remove a file from it's copy queue after successful completion of the copy.
  * when the copy resumes, it will remove foobar.tmp, and make a new one.
  * when the copy is complete, it will remove the .tmp suffix.

* do we want mtime preserved?
  * timeCopy, permCopy

### How do I know that is going on?

* look in ~/.cache/sr3/log.  Each component has a log file, will report every file noticed (in the watch) and copied (by the sender)
* sr3 status to view how the daemons are doing.

### Can we autoclean the loli uplink directory?

Once the file has been successfully transferred to hpfx, we may want to remove it
from the directory on the local linux server.

Yes. A small subscriber can be added to subscribe to successful uplinking, and could
delete the corresponding files on bob@loli. Left as an exercise.
Otoh, that would also delete upstream, see next point.

### Can we autoclean the hpfx uplink directory, from Loli?

Yes. the watch, by default, sends file removal events as well as creation.
If that is not what is desired then a line like:

```

fileEvents -delete,rmdir


```
would prevent the watch from publishing those events. This can be added
to either the watch or sender configurations (or both.)

## Do I need to Copy Files into a Hot Directory?

No. That is just a convenient interface so that users 
do not need to invoke the sr3 tools explicitly.
To save moving or copying the files locally, 
one can run two slightly different configurations, shown below:

```shell

bob@loli:~$ mkdir -p ~/.config/sr3/post
bob@loli:~$ cat >~/.config/sr3/post/queue_for_hpfx.conf <<EOT

post_broker amqps://pas037@hpfx.collab.science.gc.ca
post_exchange xs_pas037_loli_bob_queue_for_hpfx

post_baseUrl file:

nodupe_ttl on

# exclude working files (that end in .tmp)
reject .*.tmp$
accept .*
EOT

```

This makes a new poster that is not rooted at the ~/to_hpfx directory.
It creates a second exchange for a second sender to listen for these
kinds of posts (that aren't relative to the hot directory.) like so:

```shell

bob@loli:~$ cat >~/.config/sr3/sender/queue_for_hpfx.conf <<EOT
post_broker amqps://pas037@hpfx.collab.science.gc.ca
post_exchange xs_pas037_loli_bob_queue_for_hpfx

post_baseUrl file:

nodupe_ttl on

# exclude working files (that end in .tmp)
reject .*.tmp$
accept .*

bob@SSC-5CD2310S60:~/.cache/sr3/log$ more ~/.config/sr3/sender/qu*

broker amqps://pas037@hpfx.collab.science.gc.ca
exchange xs_pas037_loli_bob_queue_for_hpfx

sendTo sftp://hpfx

# while files are being uploaded, have a .tmp suffix:
inflight .tmp

nodupe_ttl on

# how many processes participate in transfer (parallelism.)
instances 1

accelThreshold 1M

# exclude working files (that end in .tmp)
reject .*.tmp$
accept .*


# tell others about uploaded files.

post_broker amqps://pas037@hpfx.collab.science.gc.ca

# channel others can subscribe to get notice when files arrive.
post_exchange xs_pas037_new_in_to_hpfx

post_baseUrl sftp://pas037@hpfx.collab.science.gc.ca/on_hpfx

# what to subtract from the path when posting
post_baseDir /home/pas037/on_hpfx

EOT

```

This sender:
* listens on a different exchange (channel)
* doesn't remove beginning of path or look for file in hot directory
* copy results in absolute path being appended under hpfx hotdir.

```shell

bob@SSC-5CD2310S60:~$ sr3 declare post/queue_for_hpfx
bob@SSC-5CD2310S60:~$ sr3 start sender/queue_for_hpfx
bob@SSC-5CD2310S60:~$ sr3 status
status:
Component/Config      Processes   Connection        Lag                              Rates
                      State   Run Retry  msg data   Que   LagMax   LagAvg   Last  %rej     pubsub   messages     RxData     TxData
                      -----   --- -----  --- ----   ---   ------   ------   ----  ----     ------   --------     ------     ------
post/queue_for_hpfx   stop    0/0     0   0%   0%     0    0.00s    0.00s      0  0.0%       0B/s       0m/s       0B/s       0B/s
sender/queue_for_hpfx idle    1/1     0 100%   0%     0    0.00s    0.00s 17m32s  0.0%       0B/s       0m/s       0B/s       0B/s
sender/to_hpfx        run     5/5     2  99%   3%     0    1.99s    1.22s  3m19s  0.0%     316B/s       0m/s       0B/s   5.1KiB/s
watch/to_hpfx         run     1/1     0 100%   0%     0    0.00s    0.00s  3m22s  0.0%       0B/s       0m/s       0B/s       0B/s
      Total Running Configs:   4 ( Processes: 10 missing: 0 stray: 0 )
                     Memory: uss:284.5MiB rss:414.4MiB vms:2.0GiB
                   CPU Time: User:1098.56s System:123.90s
           Pub/Sub Received: 1m/s (985B/s), Sent:  1m/s (535B/s) Queued: 0 Retry: 4, Mean lag: 1.22s
              Data Received: 0f/s (598B/s), Sent: 1f/s (17.0KiB/s)
bob@SSC-5CD2310S60:~$

```
Need to *declare* the exchange so that when the queue_for_hpfx sender is started, it can bind to an existing exchange
(which is created by the poster.) If that's skipped, then it will take a little while the first time 
things are started for the sender to start paying attention to events.

example, on loli do:

```shell
bob@SSC-5CD2310S60:~$ pwd
/home/bob
bob@SSC-5CD2310S60:~$ echo lala >1stfile
bob@SSC-5CD2310S60:~$ sr3_post -c queue_for_hpfx -p 1stfile
2024-12-12 14:04:06,249 [INFO] sarracenia.moth.amqp putSetup exchange declared: xs_pas037_loli_bob_queue_for_hpfx (as: amqps://pas037@hpfx.collab.science.gc.ca/)
2024-12-12 14:04:06,272 [INFO] sarracenia.flowcb.log after_accept accepted: (lag: 0.02 )  exchange: ['xs_pas037_loli_bob_queue_for_hpfx'] subtopic: home.bob a file with baseUrl: file: relPath: home/bob/1stfile id: UaNrmLF size: 5
2024-12-12 14:04:06,300 [INFO] sarracenia.flowcb.log after_post posted to exchange: xs_pas037_loli_bob_queue_for_hpfx topic: v03.home.bob a file with baseUrl: file: relPath: home/bob/1stfile size: 5 id: UaNrmLF
2024-12-12 14:04:06,301 [INFO] sarracenia.flow please_stop asked to stop
2024-12-12 14:04:06,301 [INFO] sarracenia.moth please_stop asked to stop
2024-12-12 14:04:06,301 [INFO] sarracenia.flow _runHousekeeping on_housekeeping pid: 1021822 post/queue_for_hpfx instance: 0
2024-12-12 14:04:06,304 [INFO] sarracenia.flowcb.housekeeping.resources on_housekeeping Current cpu_times: user=0.1 system=0.03
2024-12-12 14:04:06,305 [INFO] sarracenia.flowcb.housekeeping.resources on_housekeeping Current mem usage: 64.0MiB, accumulating count (1 or 1/100 so far) before self-setting threshold
2024-12-12 14:04:06,305 [INFO] sarracenia.flowcb.nodupe.disk on_housekeeping was 0, but since  0.36 sec, increased up to 1, now saved 1 entries
2024-12-12 14:04:06,305 [INFO] sarracenia.flowcb.log stats version: 3.00.56, started: now, last_housekeeping:  0.4 seconds ago
2024-12-12 14:04:06,305 [INFO] sarracenia.flowcb.log stats messages received: 1, accepted: 1, rejected: 0   rate accepted: 100.0% or 2.8 m/s
2024-12-12 14:04:06,305 [INFO] sarracenia.flowcb.log stats files transferred: 1 bytes: 5Bytes rate: 13Bytes/sec
2024-12-12 14:04:06,305 [INFO] sarracenia.flowcb.log stats lag: average: 0.02, maximum: 0.02
2024-12-12 14:04:06,305 [INFO] sarracenia.flow please_stop asked to stop
2024-12-12 14:04:06,305 [INFO] sarracenia.moth please_stop asked to stop
2024-12-12 14:04:06,305 [INFO] sarracenia.flow _runHousekeeping on_housekeeping pid: 1021822 post/queue_for_hpfx instance: 0
2024-12-12 14:04:06,309 [INFO] sarracenia.flowcb.housekeeping.resources on_housekeeping Current cpu_times: user=0.1 system=0.03
2024-12-12 14:04:06,309 [INFO] sarracenia.flowcb.housekeeping.resources on_housekeeping Current mem usage: 64.0MiB, accumulating count (1 or 1/100 so far) before self-setting threshold
2024-12-12 14:04:06,309 [INFO] sarracenia.flowcb.nodupe.disk on_housekeeping was 1, but since  0.00 sec, increased up to 1, now saved 1 entries
2024-12-12 14:04:06,309 [INFO] sarracenia.flowcb.log stats version: 3.00.56, started: now, last_housekeeping:  0.0 seconds ago
2024-12-12 14:04:06,309 [INFO] sarracenia.flowcb.log stats messages received: 0, accepted: 0, rejected: 0   rate accepted: 0.0% or 0.0 m/s
2024-12-12 14:04:06,309 [INFO] sarracenia.flowcb.log stats files transferred: 0 bytes: 0Bytes rate: 0Bytes/sec
2024-12-12 14:04:06,341 [INFO] sarracenia.flow close flow/close completed cleanly pid: 1021822 post/queue_for_hpfx instance: 0
bob@SSC-5CD2310S60:~$ 

```

Yes... it is verbose... the C version is a lot less voluble. The only useful line in this output is the *after_post* line (third one)... saying it was posted.

then can look on hpfx:
```
pas037@hpfx3:~/on_hpfx/home/bob$ cd
pas037@hpfx3:~$ ls -lR ~/on_hpfx/home
/home/pas037/on_hpfx/home:
total 4
drwxrwxr-x 2 pas037 ssc_di 4096 Dec 12 19:19 bob

/home/pas037/on_hpfx/home/bob:
total 0
-rw-r--r-- 1 pas037 ssc_di 5 Dec 12 19:19 1stfile
pas037@hpfx3:~$

```

For this case, it appends the entire absolute path after the hot directory on the destination.



# More Continuous Testing


For more involved testing, can hook up a continuous feed
see [TESTING](TESTING.md) for that. That involves installing some audit and cleanup jobs
on hpfx.
