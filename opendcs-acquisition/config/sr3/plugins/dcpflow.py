
from collections import namedtuple
import datetime
import logging
import os
import os.path
import random
import sarracenia
import sarracenia.config
from sarracenia.flowcb import FlowCB
import struct
import subprocess
import sys
import time
import urllib.request

logger = logging.getLogger(__name__)

class Dcpflow(FlowCB):
    """
      use DCStoolkit to periodically query an LRGS server, and produce files containing 1 report each (so stations are individual routable.)
      idea is produce a relatively continuous flow of messages.

      GOES - Geostationary Orbiting Environmental Satellite
      DCS - Data Communication Services, that is on GOES 
      DCSToolkit: reads DCS feeds... at a:
      LRGS:  Local Readout Ground Station.

      So there are LRGS stations which provide services on the internet that can be queried to get
      small ascii reports sent via GOES DCS by automated stations.

      https://opendcs-env.readthedocs.io/en/latest/index.html

      In the configuration files there should be lines like::

          ahlpdt SXCN40_KWAL 4541B636 457196AA 4453F6F4

      The ahlpdt option describes a mapping from the WMO-style GTS Abbreviated Header Line (AHL) also 
      known as a bulletin header, to the stations are identified by their "Platform Data Table" (PDT) 
      entry index. So the idea is to query LRGS servers for observations from the listed PDTS,
      and produce bulletins with the corresponding header. 

      there is also ahlpdt.inc an include file that includes all current associations between Pdt's and
      AHLS, which can be included in a configuration file:

         include ahlpdt.inc

      It is just a series of declarations like above.
      Which LRGS servers do we poll? these::

          lrgsUrl lrgs://username@lrgseddn1.cr.usgs.gov:16003
          lrgsUrl lrgs://username@lrgseddn2.cr.usgs.gov:16003
          lrgsUrl lrgs://username@lrgseddn3.cr.usgs.gov:16003

      Each of which should have corresponding entries in the credentials files:

          lrgs://username:password@lrgseddn1.cr.usgs.gov:16003

      The number of instances for the flow started will be one per lrgsUrl. So in the above case,
      three instances will be started, each one being assigned a primary list of stations, and
      if the following option is set:

          lrgs_download_redundancy  Yes

      then each Pdt will be downloaded from 2 LRGS servers, so that if one should fail, there is
      always a second server downloading for backup purposes.

          dcp_pdts_compressed https://dcs1.noaa.gov/PDTS_COMPRESSED.txt

      This plugin also uses nodupe_fileAgeMax to cut off the oldest query fetched.

          nodupe_fileAgeMax 600

      restrict queries to the last 10 minutes at most.

     status: 

     * it builds search criteria for getDcpMessages, spawns it, and divides the output
       into files with a give AHL.  Posts the files.
     * hiearchy missing source?

     Uses the -x and -e arguments to getDcpMessages to make splitting obs into files
     super easy, but non-printable chaaracters might be transformed by that.
     This is exactly what the old Sundew plugins did, so no worse than before.
     The Sundew plugin removed trailing spaces, tabs, and newlines. dunno why, did
     not reproduce that here.


    """

    
    def pdthdr_read(self):

        # mapping stations to abbreviated headers
        self.pdthdr = {}
        self.ahlpdt = {}
        for line in self.o.ahlpdt:
            l=line.split()
            h=l[0]
            hmap=l[1:]
            if h in self.ahlpdt:
                self.ahlpdt[h].append(hmap)
            else:
                self.ahlpdt[h]=hmap

            for p in hmap:
                self.pdthdr[p] = h

        logger.info( f" read {len(self.pdthdr)} entries read in PDT to AHL mapping table." )

    def pdt_table_read(self):
        """
            read the compressed_pdts.txt databased of platforms available on OpenDCS

            not sure of the actual source for the format of the pdt_tabl
            logic coming from Michel Grenier's "pdts_to_dictionary.py", which refers to the late Paul-Emile Bergeron 
            (the Canadian MSC Surface network GOES-DCP guy for decades.)

            FIXME: 
            there is something off somewhere in the decode... 
            the reference material I have says the records should be 242 bytes, but the records I read are only 239.
            I have decided to assume 3 less characters in the Shef_codes field (27 vs. 30)
            than what is in the documentation. Well enough of it works that can use the information for now.
        """
        logger.info( f'statedir={os.path.dirname(self.o.pid_filename)}')
        self.compressed_pdts=os.path.dirname(self.o.pid_filename)
        self.compressed_pdts=os.path.join( self.compressed_pdts, 'pdts_compressed.txt' )

        logger.info( f'compressed_pdts={self.compressed_pdts}')
        
        self.pdt_table={}

        # should download from source from time to time: https://dcs1.noaa.gov/PDTS_COMPRESSED.txt
        if not os.path.exists(self.compressed_pdts):

            if self.o.no < 2:
                try:
                    with urllib.request.urlopen( self.o.dcp_pdts_compressed ) as response:
                        f=open(self.compressed_pdts,'wb')
                        f.write(response.read())
                        f.close()
                except Exception as ex:
                    logger.error( f"failed to download {self.o.dcp_pdts_compressed}", exc_info=True )
            else:
                time.sleep(self.o.no*5)
       
        if os.path.exists(self.compressed_pdts):
            f=open(self.compressed_pdts,"rb")
            for fline in f.readlines():
                line=fline.strip()
                t=namedtuple('t', 'User_Name Pdt Prime_Type Prime_Chan Second_Type Second_Chan First_Transmit Transmit_Period ' +
                       'Transmit_Windows Transmit_Rate ' + \
                       'Data_Format Location_Code Location_Region Location_Name Latitude Longitude Category Manufacturer_Id ' + \
                       'Model_Number Season_id NMC_Flag NMC_Descriptor PMaint_Name PMaint_Phone PMaint_Fax Shef_Codes ' + \
                       'Update_Date_Year Update_Date_Date Edit_Number Complete_Flag Status' )
                #logger.info( f"len: {len(line)}, line:{line} t:{t}" )
                #                                   UnPdtyChtyCh1xXp   XwXrDfLcLrLn    LaLoCtMf Md SiNfNdMn    Mp Mf Shf   UyUdEnCfSt
                tt=t._asdict(t._make(struct.unpack("6s8s1s3s1s3s6s6s"+"4s4s1s3s1s32s"+"6s8s1s14s16s1s1s6s24s"+"20s20s27s"+"4s3s6s1s2s",line)))
                for i in tt:
                    try:
                       tt[i]=tt[i].decode('latin1')
                       if i != 'Shef_Codes':
                           tt[i]=tt[i].strip().lstrip()
                    except Exception as Ex:
                        logger.error( f'decode error, skipping... {Ex}')
                        logger.error( f"len: {len(line)}, line:{line}" )

                #logger.info( f"tuple {tt}" )
                pdt=tt['Pdt']
                del tt['Pdt']
                self.pdt_table[pdt]=tt
            f.close()
            logger.info( f" {len(self.pdt_table)} entries in Platform Definition Table read." )
        else:
            logger.error( f"missing Platformt Definition Table, please download https://dcs1.noaa.gov/PDTS_COMPRESSED.txt to {self.compressed_pdts}" )

    def pdts_setup(self):
        logger.info( f" start ")
        self.pdthdr_read()
        self.pdt_table_read()
        missing_platforms=[]
        self.good_platforms=0
        for p in self.pdthdr:
            if p in self.pdt_table:
                self.pdt_table[p]['ahl'] = self.pdthdr[p]
                self.good_platforms+=1
            else:
                missing_platforms.append(p)

        logger.info( f" end.  good: {self.good_platforms},   missing: {len(missing_platforms)}")
        if len(missing_platforms) > 0:
            missing_file=os.path.dirname(self.o.pid_filename)
            missing_file=os.path.join( missing_file, 'pdts_missing.txt' )
            f=open(missing_file, 'w' )
            f.write('\n'.join(missing_platforms)+'\n')
            f.close()
            logger.warning( f"{missing_file} contains the list of: {len(missing_platforms)} platforms not found in DCS information table (aka: pdts_compressed), probably removed/replaced ?!" )
        
    def __init__(self,options):
        logger.info('really I mean hi')

        options.add_option( 'dcp_pdts_compressed', 'str', 'https://dcs1.noaa.gov/PDTS_COMPRESSED.txt' )

        options.add_option( 'lrgsUrl', 'list', [] )
        
        options.add_option( 'lrgs_download_redundancy', 'flag', False ) 
        options.add_option( 'ahlpdt', 'list', [] )
        self.o = options

        if hasattr(self.o,'nodupe_fileAgeMax'):
            self.max_age_in_minutes = int(self.o.nodupe_fileAgeMax/60)


    def on_start(self):

        self.lrgs_servers=[]
        for server_url in self.o.lrgsUrl:
            ok, parsed_url = self.o.credentials.get(server_url)
            if ok:
                self.lrgs_servers.append(parsed_url)
            else:
                logger.error( f"no credentials entry found for {server_url}, Cannot use" )

        if self.o.instances != len(self.lrgs_servers):
            logger.critical( f"instances option must match number of lrgsUrl entries (each instance queries one lrgsUrl)" )

        if self.o.no > 0:
            self.lrgs_server = self.lrgs_servers[ self.o.no-1 ].url
        else:
            self.lrgs_server = self.lrgs_servers[ 0 ].url

        logger.info( f"this instance will poll {self.lrgs_server} " )

        self.pdts_setup()

    def generate_message( self, BulletinFile, Pdt ):
        bulletin_stat = sarracenia.stat( BulletinFile )
        msg = sarracenia.Message.fromFileData(BulletinFile, self.o, bulletin_stat)

        if Pdt in self.pdt_table:
            logger.critical( f" table entry: {self.pdt_table[Pdt]} " )
            
            try:
                lat=float(self.pdt_table[Pdt]['Latitude'])/10000
                lon=float(self.pdt_table[Pdt]['Longitude'])/10000
                logger.critical( f"lat: {lat}, lon: {lon} " )
                if (lat != 0) or (lon != 0):
                    msg['geometry'] = { 'type': 'Point', 'coordinates': ( lat, lon ) }
                logger.critical( f" msg: {msg} " )
            except Exception as ex:
               pass
        return msg

    def gather(self):
        """
           return new messages.
        """

        # define selection criteria for getDcpMessages.
        self.MessageBrowser=os.path.dirname(self.o.pid_filename)
        self.MessageBrowser=os.path.join( self.MessageBrowser, f'MessageBrowser-{self.o.no}.sc' )
        
        self.LastGoodQuery=os.path.dirname(self.o.pid_filename)
        self.LastGoodQuery=os.path.join( self.LastGoodQuery, f'LastGoodQuery-{self.o.no}.timestamp' )
            
        if os.path.exists(self.LastGoodQuery):
            lastGoodStat=os.stat(self.LastGoodQuery)
            last_minute= int((time.time() - lastGoodStat.st_mtime)/60+1)
        else:
            last_minute=5
        if last_minute > self.max_age_in_minutes:
            last_minute=self.max_age_in_minutes

        mbf = open( self.MessageBrowser, 'w')
        mbf.write( f"DRS_SINCE: now - {last_minute} minutes\n" )
        mbf.write( "DRS_UNTIL: now\n" )

        counter=1
        #for p in self.pdt_table:
        for p in self.pdthdr:
            # primary
            if (self.o.no == 0) or (counter % self.o.instances == (self.o.no-1)) :
                mbf.write( f"DCP_ADDRESS: {p}\n" )
            # backup
            elif self.o.lrgs_download_redundancy and ((counter+1) % self.o.instances == (self.o.no-1)) :
                mbf.write( f"DCP_ADDRESS: {p}\n" )
            counter += 1
        mbf.close()


        #getDcpMessages -h server -p port -u username -P password -f MessageBrowser.sc
        lsu=self.lrgs_server
        rawObsFile=os.path.join( os.path.dirname(self.MessageBrowser), f"rawObs-{self.o.no}.txt" )

        # options omitted from Sundew version (to make more accurate WMO bulletins)
        cmd= f"/usr/bin/bash {os.getenv('DCSTOOL_HOME')}/bin/getDcpMessages -x -e -bTTAAii -h {lsu.hostname} -p {lsu.port} -u {lsu.username} -P {lsu.password} -f {self.MessageBrowser}".split()

        # FIXME... thinking about more elegant test harnesses.
        # set to True to debug previously downloaded data without spamming LRGS server.
        if True:
            logger.critical( f"using canned data instead of {cmd}" )
        else:
            rof=open(rawObsFile,'w')
            p=subprocess.Popen(cmd,stdout=rof)
            p.wait()
            rof.close()
            if p.returncode == 0:
                with open( self.LastGoodQuery, 'w' ) as f:
                    f.write( f"{os.getpid()}\n" )
                logger.info( f"ran {cmd} successfully")
            else:
                logger.error( f"{cmd}: failed")
                return []

        rof=open(rawObsFile,'r')
        FirstLine=False
        bf=None
        messages=[]
        RxTime=datetime.datetime.now(datetime.timezone.utc)
        for raw_line in rof.readlines():
            if raw_line.startswith("TTAAii"):
                FirstLine=True
                if bf:
                     bf.close()
                     messages.append(self.generate_message(BulletinFile,Pdt))
                continue
            elif FirstLine:
                FirstLine = False
                # ........YYjjjhhmm
                # 012345678901234567
                # 45A1A0CA23192023741
                try:
                    Pdt=raw_line[0:8]
                    Ahl=self.pdthdr[Pdt]
                    ob_time = datetime.datetime.strptime( raw_line[8:17], "%y%j%H%M" )
                    dd="%02d" % ob_time.day
                    hh=raw_line[13:15]
                    mm=raw_line[15:17]
                    rnd="%05d" % random.randint(1,10000)

                    subdir=os.path.join( self.o.variableExpansion(self.o.directory), \
                            f"{RxTime.year}{RxTime.month:02d}{RxTime.day:02d}", f"{self.o.source}", \
                            f"{Ahl[0:2]}", f"{Ahl[7:]}", f"{hh}" )
                    if not os.path.isdir( subdir ):
                        os.makedirs( subdir ) 

                    BulletinFile=os.path.join( subdir, f"{Ahl}_{dd}{hh}{mm}_{rnd}" )
                    bf=open(BulletinFile,'w')
                    logger.info( f"writing: {BulletinFile}" )
                    bf.write( f"{Ahl.replace('_',' ')} {dd}{hh}{mm}\r\r\n" )
                except Exception as ex:
                    logger.error( "problem reading ob", exc_info=True )
                    continue
            bf.write(raw_line)

        if bf:
            bf.close()
            messages.append(self.generate_message(BulletinFile,Pdt))
        rof.close()

        return messages

#logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

#logger.info('hello')
#options = sarracenia.config.Config()
#hoho=Dcpflow(options)
#logger.info('goodbye')

