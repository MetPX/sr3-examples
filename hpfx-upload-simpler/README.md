
# Hot Directory to Upload Files to a Cluster  

Purpose:
* Private, per user transfers from one local(ish) server to a relatively remote compute cluster.
* files are encrypted in transit (using sftp/scp/ssh transfers.)

**Presume:**

* we have someone handy with linux command line.
* we have a local linux server, with access to large data sets 
* we have a cluster (called hpfx), or data centre with a lot of storage.
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


copy the loli\_config tree from the example folder to ~/.config/sr3

```shell


bob@loli:~$ mkdir -p ~/to_hpfx  # local uplink directory for files destined for hpfx.
bob@loli:~$ mkdir -p ~/.config/

bob@loli:~$ ssh hpfx.collab.science.gc.ca -c 'mkdir -p ~/on_hpfx' # directory to store files in.

```

Note that ~/to_hpfx needs to be in a file system with enough space to hold all 
the files expected to transit through it.

Cleanup of this directory after transfer is complete is outside the 
scope of this exercise.

### write the amqp auth information to a local credential store:

    echo amqps://pas037:pas037_password@hpfx.collab.science.gc.ca >>~/.config/sr3/credentials.conf

This is a line to store broker credentials to allow message publishing and subscribing.

This line:
  * pas037 is the CLUSTER_AMQP_USER
  * hostname is CLUSTER_AMQP_BROKER
  * no variable substitutions allowed. Literal values needed.


### Install the Configuration Files.

```shell 

bob@loli:-$  cp loli_config/sr3 ~/.config/sr3
bob@loli:~$  vi ~/.config/sr3/default.conf

```

The values in default.conf need to be modified for the hosts and clusters targetted:

```

# Upload Location Settings.

# one must have passwordless access to the remote cluster.
# typically a nickname in the ~/.ssh/config is needed here
#
declare env CLUSTER_SSH_HOSTNAME=hpfx
declare env CLUSTER_SSH_USERNAME=pas037

# the folder on the cluster where files are sent.
# there needs to be enough space there.
declare env CLUSTER_SSH_FOLDER=/home/${CLUSTER_SSH_USERNAME}/on_${CLUSTER_SSH_HOSTNAME}


# Local File Settings:

# UPLOADING_HOST is a good name for the source being uploaded from.
# it's a display/documentation name... meant to help finding related
# resources when debugging.
declare env UPLOADING_HOST=loli

# the unix username on the UPLOADING host being used to run the daemons.
declare env UPLOADING_HOST_USER=bob

# can be overridden, but default ok.
declare env UPLOADING_HOST_FOLDER=/home/${UPLOADING_HOST_USER}/to_${CLUSTER_SSH_HOSTNAME}



# Transfer Management Settings

# A message queueing server where notifications of new files to upload are published
# the messages are published in the AMQP protocol.
#
declare env CLUSTER_AMQP_BROKER=hpfx.collab.science.gc.ca

# often broker user and ssh user names are the same.
# but not always.
declare env CLUSTER_AMQP_USER=${CLUSTER_SSH_USERNAME}

# exchange where the messsages about new files to upload are published.
# can be overridden, but default ok.
declare env UPLOADING_EXCHANGE=xs_${CLUSTER_AMQP_USER}_from_${UPLOADING_HOST}_${UPLOADING_HOST_USER}_
to_${CLUSTER_SHORT_NAME}

# exchange where messages about new files are published after upload is done.
# can be overridden, but default ok.
declare env CLUSTER_EXCHANGE=xs_${CLUSTER_AMQP_USER}_on_${CLUSTER_SHORT_NAME}

```

```shell
bob@loli:-$  sr3 declare

```

*sr3 declare* should connect to the broker and declare the exchange the watch
will be posting to. If the declare does not succeed, stop here
and debug until it does.


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


### How do I know that is going on?

* look in ~/.cache/sr3/log.  Each component has a log file, will report every file noticed (in the watch) and copied (by the sender)
* sr3 status to view how the daemons are doing.


### Can we autoclean the hpfx uplink directory, from Loli?

With the given configuration, no, file removals are not forwarded. 
If that is not what is desired then comment the fileEvents line:

```

#fileEvents -delete,rmdir


```

would have the watch from publishing those events. This can be added
to either the watch or sender configurations (or both.) In that case,
deletion at source will result in deleting at the other end as well.
