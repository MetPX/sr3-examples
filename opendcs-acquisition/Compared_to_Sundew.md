

# Comparison with Sundew Integration

Please do not interpret anything here as a critique of what was done for the Sundew and OpenDCS integration.
That work was done incrementally many several years with no clear understanding of the systems at the outset.
The Sarracenia work is instead undertaken with full knowledge of what was done before, and with a very
clear idea of what is needed, so it is naturally affords many opportunities for improvement.


comparison of work in terms of complexity, Sundew:

```
fractal% find . -name '*.sh' -o -name '*.conf' -o -name '*.py' | xargs wc -l
     2 ./etc/lrgsRouting.conf
  5105 ./etc/lrgs_pdt2hdr.py
    42 ./etc/tx/.archive/2015/ddi1-kwal.conf
    28 ./etc/tx/.archive/2015/dd-notify-ddi1.conf
    28 ./etc/tx/.archive/2015/dd-notify-ddi2.conf
    42 ./etc/tx/.archive/2015/ddi2-kwal.conf
    22 ./etc/tx/sundewBackend.conf
   180 ./etc/fileRouting.conf
     0 ./etc/stations_SA.conf
    13 ./etc/wmo_id.conf
  5106 ./etc/scripts/lrgs_pdt2hdr.py
   199 ./etc/scripts/.archive/pull-lrgs-observations.py
   393 ./etc/scripts/metpx_sr_post_parts.py
    23 ./etc/scripts/getDcpMessages.sh
   255 ./etc/scripts/pull-lrgs-observations.py
   293 ./etc/scripts/metpx_sr_post.py
   696 ./etc/scripts/SenderFTP.py
    36 ./etc/fx/cvt_lrgs_to_bulletin.conf
     0 ./etc/stations_TAF.conf
    25 ./etc/rx/pull-site-lrgseddn3.conf
    26 ./etc/rx/pull-site-lrgseddn1.conf
    25 ./etc/rx/pull-site-lrgseddn2.conf
     0 ./etc/stations_FD.conf
   215 ./scripts/pdts_to_dictionary.py
    93 ./scripts/create_pdts_pdt2hdr.py
    24 ./scripts/check_incoming_pdt.sh
    29 ./scripts/build_pdt_request.py
   166 ./sftp_amqp4.py
 13066 total

```

comparable information for the Sarra plugin version:

```

fractal% find . -type f |xargs wc -l
  209 ./INSTALL.md
   43 ./config/sr3/flow/pull-USGS_LRGS.conf
  351 ./config/sr3/flow/ahlpdt.inc
  369 ./config/sr3/plugins/dcpflow.py
   48 ./Compared_to_Sundew.md
 1020 total
fractal% 

```

So, about 10x less stuff to manage.

* Configuration files are smaller (bulletin association with PDT is more concisely expressed.)
* Sarracenia provides much more built-in functionality, the only code here is to interface with OpenDCS
* The Sundew plugin had to implement AMQP, building messages manually, and various availability strategies with stuff being left around from previous attempts.
* In the Sarracenia plugin, availability is implemented with two lines of code in producing the query selection criteria instead of an array of scripts.
* Sundew's pxRouting table, which is also needed, was left out from the comparison (it's 104klines... would have dwarfed everything else.)
* the maintenance interventions in Sarracenia are straightforward, edit one file, and restart. in Sundew, one has to re-run a sort
  of compiler to rebuild configurations as an intermediate step.
* in the Sundew version one must have one configuration per LRGS server, the Sarracenia plugin uses a single configuration to query all three with redundancy included.
* The Sarracenia version sanity checks PDTs, noting the ones missing from the OpenDCS reference, for later resolution.



