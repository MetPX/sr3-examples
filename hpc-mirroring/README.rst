
STATUS: INCOMPLETE ... This example is a work in progress. Not complete yet.

HPC Mirrorring
==============

This example demonstrates what is needed to mirror a very large, very dynamic
directory tree to another one (conventionally on another file system.)  The 
purpose of this mirroring is:

* to have a copy on a second device in case the primary one becomes unavailable.
  Note that this means when availability is restored, we want to mirror
  in the opposite direction to restore it.

* To have a copy that can be used to non-critical uses, isolating/reducing
  io load on the source device.  
  (also providing faster access for those for whom the destination device is 
   local.)

All computing is presumed to be in Linux environment.

This is not an administrative service, but one run by a single user
to mirror their own files. There are no root functions used to implement
this service, other than setting up the services to permit access
by the user.


Stuff 
-----

What needs to be existing for this solution to apply?

1. Two high performance computing clusters (HPC)

   The clusters have multiple nodes, we'll just abstract them as clustername node number.

   * hpc1nX
   * hpc2nX


2. A user account, or pair of user account credentials to be able to access each cluster.

   * opsM - the ops Mirror user.

   The user can access all of the files to be read from the source.


3. A high speed network between them.

   Network speed will provide an upperbound on transfer speed.

   * on hpc2nX one should be able to ssh opsM@hpc1nY
   
   * When we don't care about the value of X, there should be 
     network alias we can use e.g.: hpc1any (for any node in hpc1)

   * In some HPC clusters, there are designated nodes for io,
     and only those nodes can receive/initiate external ssh connections.
     If that is the case then for the purpose of this discussion,
     those are the only nodes being referenced.

4. two file systems, 

   * /fs/primary/
   * /fs/secondary/
   
5. A message broker (perhaps a pair or trio with HA setup...) 
   note: HA broker setup is outside the scope of this example.
   will just use a single one.

   * amqps://opsM@mybroker

6. The metpx-sr3c (C implementation) package (to provide the *shim library*)  (>= 3.24.12)
   installed on both clusters: https://github.com/MetPX/sarrac/releases

7. the metpx-sr3 (Python implementation) package (to provide the winnow, and subscriber 
   installed on both clusters:  https://github.com/MetPX/sarracenia/releases (>= 3.0.57)

8. Users willing to tweak their jobs/scripts to deal with limitations
   of this method or mirroring.



Setup
-----

* install a local broker (outside scope... FIXME point to existing recipe.)

```

./create_test_dirs.sh


```

This creates /tmp/source, /tmp/destination, and ~/fakeplace/user pointing to /tmp/source/realplace/user

```

./install_sr3_configs.sh
sr3 declare cpost/mirror
sr3 start


```
install the sr3 flow configurations for mirroring:

```
fractal% sr3 status
status:
Component/Config     Processes                                         Rates
                     State   Run Retry  Que     Lag    Last    %rej  messages      Data
                     -----   --- -----  ---     ---    ----    ----  --------      ----
                     cpost/mirror         stop    0/0    -    -       -      -       -       -           -
sarra/mirror_copy    idle  10/10    0    0    0.00s   n/a    0.0%     0m/s       0B/s
shovel/mirror_tally  idle    1/1    0    0    0.00s   n/a    0.0%     0m/s       0B/s
winnow/mirror00      idle    1/1    0    0    0.00s   n/a    0.0%     0m/s       0B/s
winnow/mirror01      idle    1/1    0    0    0.00s   n/a    0.0%     0m/s       0B/s
winnow/mirror02      idle    1/1    0    0    0.00s   n/a    0.0%     0m/s       0B/s
winnow/mirror03      idle    1/1    0    0    0.00s   n/a    0.0%     0m/s       0B/s
winnow/mirror04      idle    1/1    0    0    0.00s   n/a    0.0%     0m/s       0B/s
      Total Running Configs:   7 ( Processes: 16 missing: 0 stray: 0 )
                     Memory: uss:705.7MiB rss:936.8MiB vms:1.4GiB
                   CPU Time: User:6.41s System:1.11s
	   Pub/Sub Received: 0m/s (0B/s), Sent:  0m/s (0B/s) Queued: 0 Retry: 0, Mean lag: 0.00s
	      Data Received: 0f/s (0B/s), Sent: 0f/s (0B/s)

fractal%


```

* cpost/mirror - configuration of shim library used to post files in the source tree.
* winnow/mirror0x - filtering of *noise* by delaying copies for 30 seconds between source and destination.
* sarra/mirror_copy - the jobs that copy data from source to destination.
* shovel/mirror_tally - count up the amount of data transferred from source to destination.

We will call this session the management shell. In another shell (call it shim shell), run a typical 
job in a user directory that is linked into the source tree:

```
 iedir=`pwd`
 cd ~/fakeplace/${USER}
 ${iedir}/run_profile.sh

```
Now an commands run in this shell that write files should generate posts, and about a little over 30 seconds later
copies will happen. e.g.:

```
  git clone https://github.com/torvalds/linux >git_clone.log 2>&1 &

```

This will take many minutes (15?) to run (limited by network bandwidth.) and create many files in the source tree.
Those files will be copied to the destination tree.

In the management shell can check how the mirroring went:

```

fractal% ./audit_mirror.sh
Comparing contents of /tmp/source and /tmp/destination
running audit...
audit complete.
3 Differences between files in source and desination
0a1,2
> c8f39b6465a9c18b4047940305d39ef5  /home/peter/.python_history
> bc24a1268dbb2431045c38ff68c9a29e  /home/peter/.viminfo
0 Differences between links in source and desination
fractal%


```



