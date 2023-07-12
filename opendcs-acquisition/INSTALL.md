
# Circulating Observations obtained via GOES DCS as Bulletins

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

* *post_broker* *post_exchange* to match the broker and,
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


