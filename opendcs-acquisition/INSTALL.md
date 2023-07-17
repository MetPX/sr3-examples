
# Circulating RAW GOES DCS Observations obtained via LRGS as Bulletin Files.

Firstly, follow the instructions to download/install OpenDCS https://github.com/opendcs/opendcs/.
Only the initial installation is needed, the daemons are not needed, nor does anything need
to be running. The only component used in this example is *getDcsMessages* which is used
to query remote LRGS servers.  

The rest of the OpenDCS setup is used to configure a local LRGS server (assuming you have the requisite
satellite dish) and serve the data to internet users. That is standard LRGS stuff outside the scope
of this example which just covers importing LRGS/DCS data for use in WMO GTS style message flows through
Sarracenia networks.

You will need:

* A linux server. This work was done on an ubuntu 22.04 server.
* metpx-sr3 >= 3.0.41 installed.
* a username and password for the broker you intend to post to (could be installed yourself
  or obtained from someone else.)
* a username and password from the LRGS Servers you plan to query.

```

sudo apt install default-jre

# (on a graphical desktop, because setup requres X)

wget https://github.com/opendcs/opendcs/releases/download/7.0.8/opendcs-ot-7.0.8.jar

java -jar opendcs-ot-7.0.8.jar


# put it in ${HOME}/opendcs

cat >${HOME}/opendcs/env.sh <<EOT

DCSTOOL_HOME=${HOME}/opendcs
export DCSTOOL_HOME

if [ -d $DCSTOOL/bin ]; then
    PATH=$DCSTOOL_HOME/bin:$PATH
fi
export PATH

EOT

. ${HOME}/opendcs/env.sh

```

```

mkdir -p ~/.config/sr3/flow
cp config/sr3/plugins/dcpflow.py ~/.config/sr3/plugins
cp config/sr3/flow/pull-USGS_LRGS.conf ~/.config/sr3/flow

```

Look at the lrgsUrl lines in the configuration file.  Access to those servers is authenticated,
so one needs to set the correct user in those Urls, and add entries to ~/.config/sr3/credentials.conf
with the same url, but including the password. so entry in the configuration file:

```
lrgsUrl lrgs://user@server:port

```
in credentials.conf there should be a corresponding line:

```

lrgs://user:password@server:port

```

Also in the ~/.config/sr3/pull-USGS_LRGS.conf configuration file there is a line:

```

declare env DCSTOOL_HOME=${HOME}/opendcs


```

This may require adjustment to reflect where the DCS Toolkit was installed in the first step.

In order to publish the reports obtained, there needs to be a broker to publish to. One
can use the existing examples ../empty-amqp-broker or ../empty-mqtt-broker to make a broker
available on localhost, or use some pre-existing broker. Once the broker is available,
the following options in the installed configuration will require adjustment:

* *post_broker* and *post_exchange* to match the broker and,
* *post_baseUrl* to match the file transfer protocol in use.

Placement on local disk is managed with:

* *directory* the local file system where the files will be written

Lastly, The way this pull flow works is to issue queries to the LRGS server about specific PDT's.
those are automated stations that uplink to the GOES Satellites using the Data Communications Service (DCS)
When this flow writes a file, it turns it into something routable on a WMO GTS network by putting
a GTS Header on it. There is a mapping file with lines like:

````
   ahlpdt SXCN40_KWAL 44419178 4443A116 45464486 7D0422D4 45A2B4B2

````

The header is SXCN40_KWAL and the stations whose observations will be published under that header are the eight digit
identifiers to the right on the line. The list of the ahlpdts define the list of PDTS to ask the LRGS servers about.
For example, If the LRGS server has a current report for 45464486, the flow will download the data from the LRGS 
server and put it in a file with a header like SRCN40 KWAL YYGGgg and the file name will be similar with a randomized
suffix to avoid name clashes.

While a sample of the ahlpdts' used to retrieve a heck of a lot of Canadian observations is provided in
config/sr3/flow/ahlpdt.inc, it is highly likely that a different user would want to produce their own version
of that file to match the platforms they are interested in.

Note that in the Canadian version, the KWAL origin is used (which normally represents Wallopps Island's LRGS Server)
because this is a backup for the data normally obtained via GTS from Wallopp's island. The names are the same
to avoid all consumers having to allow for different origins in the primary or backup case. This is a fairly special
case, and most uses would involve discussion with the local GTS authority to select proper headers for the bulletins.



## Sample run:

```

fractal% sr3 start flow/pull-USGS_LRGS.conf
missing state for flow/pull-USGS_LRGS
starting:.( 3 ) Done

fractal% 


```

sample log of an instance:

```

ractal% more flow_pull-USGS_LRGS_01.log
2023-07-12 12:55:26,242 [INFO] sarracenia.flow loadCallbacks flowCallback plugins to load: ['sarracenia.flowcb.retry.Retry', 'sarracenia.flowcb.ho
usekeeping.resources.Resources', 'dcpflow', 'log', 'post.message']
2023-07-12 12:55:26,243 [INFO] sarracenia.config add_option retry_driver declared as type:<class 'str'> value:disk
2023-07-12 12:55:26,253 [INFO] sarracenia.config add_option MemoryMax declared as type:<class 'int'> value:0
2023-07-12 12:55:26,253 [INFO] sarracenia.config add_option MemoryBaseLineFile declared as type:<class 'int'> value:100
2023-07-12 12:55:26,253 [INFO] sarracenia.config add_option MemoryMultiplier declared as type:<class 'float'> value:3
2023-07-12 12:55:26,254 [INFO] dcpflow __init__ really I mean hi
2023-07-12 12:55:26,254 [INFO] sarracenia.config add_option dcp_pdts_compressed declared as type:<class 'str'> value:https://dcs1.noaa.gov/PDTS_CO
MPRESSED.txt
2023-07-12 12:55:26,254 [INFO] sarracenia.config add_option lrgsUrl declared as type:<class 'list'> value:['lrgs://wsccmc@lrgseddn1.cr.usgs.gov:16
003', 'lrgs://wsccmc@lrgseddn2.cr.usgs.gov:16003', 'lrgs://wsccmc@lrgseddn3.cr.usgs.gov:16003']
2023-07-12 12:55:26,254 [INFO] sarracenia.config add_option lrgs_download_redundancy declared as type:<class 'bool'> value:Yes
2023-07-12 12:55:26,254 [INFO] sarracenia.config add_option ahlpdt declared as type:<class 'list'> value:['SXCN40_KWAL 4541B636 457196AA 4453F6F4 
4454A4BC 44 ...
2023-07-12 12:55:26,258 [INFO] dcpflow pdts_setup  start 
2023-07-12 12:55:26,259 [INFO] dcpflow pdthdr_read  read 5105 entries read in PDT to AHL mapping table.
2023-07-12 12:55:26,259 [INFO] dcpflow pdt_table_read statedir=/home/peter/.cache/sr3/flow/pull-USGS_LRGS
2023-07-12 12:55:26,259 [INFO] dcpflow pdt_table_read compressed_pdts=/home/peter/.cache/sr3/flow/pull-USGS_LRGS/pdts_compressed.txt
2023-07-12 12:55:38,928 [INFO] dcpflow pdt_table_read  43354 entries in Platform Definition Table read.
2023-07-12 12:55:38,932 [INFO] dcpflow pdts_setup  end.  good: 4214,   missing: 891
2023-07-12 12:55:38,932 [WARNING] dcpflow pdts_setup /home/peter/.cache/sr3/flow/pull-USGS_LRGS/pdts_missing.txt contains the list of: 891 platfor
ms not found in DCS information table (aka: pdts_compressed), probably removed/replaced ?!
Until time reached. Normal termination
2023-07-12 12:55:45,103 [INFO] dcpflow gather ran ['/usr/bin/bash', '/home/peter/opendcs/bin/getDcpMessages', '-x', '-e', '-bTTAAii', '-h', 'lrgse
ddn1.cr.usgs.gov', '-p', '16003', '-u', 'user', '-P', 'password', '-f', '/home/peter/.cache/sr3/flow/pull-USGS_LRGS/MessageBrowser-1.sc'] su
ccessfully

  .
  .
  .

2023-07-12 12:55:45,104 [INFO] dcpflow gather writing: /tmp/hoho/20230712/USGS_LRGS/SX/KWAL/16/SXAK50_KWAL_121650_02983
2023-07-12 12:55:45,107 [CRITICAL] dcpflow generate_message  table entry: {'User_Name': 'NWSARH', 'Prime_Type': 'S', 'Prime_Chan': '216', 'Second_
Type': 'U', 'Second_Chan': '000', 'First_Transmit': '000030', 'Transmit_Period': '000500', 'Transmit_Windows': '0010', 'Transmit_Rate': '0300', 'D
ata_Format': 'A', 'Location_Code': 'ZZ', 'Location_Region': 'U', 'Location_Name': '', 'Latitude': '000000', 'Longitude': '0000000', 'Category': 'U
', 'Manufacturer_Id': 'UNKNOWN', 'Model_Number': 'UNKNOWN', 'Season_id': 'N', 'NMC_Flag': 'Y', 'NMC_Descriptor': 'SXAK50', 'PMaint_Name': 'CUSTER,
KIM', 'PMaint_Phone': '907 790-6812', 'PMaint_Fax': '', 'Shef_Codes': '                           ', 'Update_Date_Year': '2', 'Update_Date_Date': 
'012', 'Edit_Number': '324000', 'Complete_Flag': '1', 'Status': '6N', 'ahl': 'SXAK50_KWAL'} 
2023-07-12 12:55:45,107 [CRITICAL] dcpflow generate_message lat: 0.0, lon: 0.0 
2023-07-12 12:55:45,107 [CRITICAL] dcpflow generate_message  msg: {'_format': 'v03', '_deleteOnPost': {'new_dir', 'exchange', 'post_format', '_for
mat', 'new_file', 'new_baseUrl', 'new_subtopic', 'new_relPath', 'local_offset', 'subtopic'}, 'exchange': ['xs_lrgs_bulletins'], 'local_offset': 0,
 'pubTime': '20230712T165545.105057955', 'new_dir': '/tmp/hoho/20230712/USGS_LRGS/SX/KWAL/16', 'new_file': 'SXAK50_KWAL_121650_02983', 'post_forma
t': 'v03', 'new_baseUrl': 'file:/tmp/hoho', 'new_relPath': '20230712/USGS_LRGS/SX/KWAL/16/SXAK50_KWAL_121650_02983', 'new_subtopic': ['20230712', 
'USGS_LRGS', 'SX', 'KWAL', '16'], 'relPath': '20230712/USGS_LRGS/SX/KWAL/16/SXAK50_KWAL_121650_02983', 'subtopic': ['20230712', 'USGS_LRGS', 'SX',
 'KWAL', '16'], 'baseUrl': 'file:/tmp/hoho', 'source': 'USGS_LRGS', 'mode': '664', 'size': 245, 'mtime': '20230712T165545.101619482', 'atime': '20
230712T165545.101619482', 'identity': {'method': 'sha512', 'value': 'cMRf2vrB+S7sL1UlNfjPnupgqkkYflyxKNx870HuGQA6+YjpI0ismIYF5FAGlyRU7V9yT9W/ntBgE
XsBIUqHIg=='}, 'contentType': 'text/plain'} 
2023-07-12 12:55:45,107 [INFO] dcpflow gather writing: /tmp/hoho/20230712/USGS_LRGS/SX/KWAL/16/SXMF40_KWAL_121650_04198
2023-07-12 12:55:45,109 [CRITICAL] dcpflow generate_message  table entry: {'User_Name': 'IPGPFR', 'Prime_Type': 'S', 'Prime_Chan': '219', 'Second_
Type': 'U', 'Second_Chan': '000', 'First_Transmit': '000040', 'Transmit_Period': '000500', 'Transmit_Windows': '0010', 'Transmit_Rate': '0300', 'D
ata_Format': 'A', 'Location_Code': 'MQ', 'Location_Region': 'O', 'Location_Name': 'LE ROBERT', 'Latitude': '000015', 'Longitude': '-0000061', 'Cat
egory': 'L', 'Manufacturer_Id': 'OTT', 'Model_Number': 'OTT HDR', 'Season_id': 'N', 'NMC_Flag': 'Y', 'NMC_Descriptor': 'SOMR10', 'PMaint_Name': 'D
EROUSSI,SÉBASTIEN', 'PMaint_Phone': '+590 590 99 11 47', 'PMaint_Fax': '+590 590 99 11 34', 'Shef_Codes': 'HMPLVB                     ', 'Update_D
ate_Year': '2', 'Update_Date_Date': '021', 'Edit_Number': '350000', 'Complete_Flag': '0', 'Status': '5N', 'ahl': 'SXMF40_KWAL'} 

  .
  .
  .

eventually it gets posted:

2023-07-12 13:02:10,599 [INFO] sarracenia.flowcb.log after_post posted {'_format': 'v03', '_deleteOnPost': {'new_dir', 'old_format', '_format', 'local_offset', 'post_format', 'new_relPath', 'new_subtopic', 'new_file', 'new_baseUrl', 'subtopic', 'exchange'}, 'exchange': ['xs_lrgs_bulletins'], 'local_offset': 0, 'pubTime': '20230712T170210.59493351', 'new_dir': '/tmp/hoho/20230712/USGS_LRGS/SR/KWAL/17', 'new_file': 'SRMN20_KWAL_121700_07628', 'post_format': 'v03', 'new_baseUrl': 'file:/tmp/hoho', 'new_relPath': '20230712/USGS_LRGS/SR/KWAL/17/SRMN20_KWAL_121700_07628', 'new_subtopic': ['20230712', 'USGS_LRGS', 'SR', 'KWAL', '17'], 'relPath': '20230712/USGS_LRGS/SR/KWAL/17/SRMN20_KWAL_121700_07628', 'subtopic': ['20230712', 'USGS_LRGS', 'SR', 'KWAL', '17'], 'baseUrl': 'file:/tmp/hoho', 'source': 'USGS_LRGS', 'mode': '664', 'size': 156, 'mtime': '20230712T170210.587805271', 'atime': '20230712T170210.587805271', 'identity': {'method': 'sha512', 'value': 'X2BbnMgBch0XkvST/w0dvbDa/N8TXm8q6ngV+whNT6ulIo+3kUY1mL1yZEyQQ0mMmrfh5wD6uWnrrcksDhHNVw=='}, 'contentType': 'text/plain', 'geometry': {'type': 'Point', 'coordinates': (47.1356, -93.3148)}, 'old_format': 'v03'}


```

## Data Encoding

* based on python string method: .decode('unicode-escape') expands all the \077 octal characters to ASCII equivalents.
* replace \r and \n with line-feed and carriage-return respectively.
* trip trailing spaces on each line.
* ignore \f (formfeed) and \t (tab) and any other escape codes.
* not sure what happens with \\ I think nothing.


## Maintenance Activities

### Robustness to single LRGS Server failure

The *lrgsUrl* configuration setting determines which remote server to query for observations. The flow will run
one process instance to query each configured server, so the number of *instances* should be configured to match
the number of *lrgsUrl* entries in the configuration file.

The *lrgs_download_redundancy* option configures search criteria so that every observation is requests from two servers.

Since all observations are downloaded from two servers, the failure of any single server will not result in any
data loss.


### Add a station

find the PDT of the station to be added, add it to the appropriate header in ~/.config/sr3/flow/ahlpdt.inc
restarting the flow will have the change take effect

### Remove a station

edit ~/.config/sr3/flow/ahlpdt.inc to remove the entry.
restart the flow to have it take effect.

### Get new station definitions from OpenDCS.

Remove the local cached copy, and it will be download automatically at the next restart:

```

rm ~/.cache/sr3/flow/pull-LRGS_USGS/pdt_compressed.txt
sr3 restart flow/pull-LRGS_USGS

```

restart the flow, it will download the latest version during startup.


## Opportunities

This is a directish port of the work done 15 years ago for MetPX Sundew to the new Sarracenia 
version 3 technology. It uses the same methods as that old 
