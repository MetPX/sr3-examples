
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

6. the metpx-sr3c (C implementation) package (to provide the *shim library*) 
   installed on both clusters: https://github.com/MetPX/sarrac/releases

7. the metpx-sr3 (Python implementation) package (to provide the winnow, and subscriber 
   installed on both clusters:  https://github.com/MetPX/sarracenia/releases

8. Users willing to tweak their jobs/scripts to deal with limitations
   of this method or mirroring.



Configurations
--------------


Posting
~~~~~~~

For the shim library:

```

cat >~/.config/sr3/cpost/shim_mirror_primary.conf <<EOT

EOT

```

for the shell environment (e.g. ~/.bashrc? ~/.bash_profile) :

```



```


Winnowing
~~~~~~~~~





Copying
~~~~~~~
