import logging
from sarracenia import timeflt2str, timestr2flt, durationToSeconds
from sarracenia.flowcb import FlowCB

logger = logging.getLogger(__name__)

class Every_rad(FlowCB):
    """

       complain if a file is missing, assuming:
        - files arrive every 6 minutes.
        - the naming convention below.
        - based on date/time from the file names.
        - give 2 minutes grace.

       Sample file name:
           202412112012_CASMA_CAPPI_1.0_SNOW_A11Y.gif

           split into:
           202412112012 and CASMA_CAPPI_1.0_SNOW_A11Y.gif

           m['new_file'][13] == '_'
           this_time = m['new_file'][0:12]
           this_file = m['new_file'][14:]

           last_radar_received[ 'CASMA_CAPPI_1.0_SNOW_A11Y.gif' ] = 202412112012
    """

    def __init__(self, options):
        super().__init__(options,logger)

        self.last_radar_received = {}

        grace=120 #durationToSeconds("2m")
        self.max_product_interval=grace+360 #durationToSeconds("6m")+grace

    def after_accept(self, worklist):
        for m in worklist.incoming:

           if m['new_file'][12] != '_' :
               logger.error( f"malformed filename, expected 12 character date-time at start {m['new_file']}")
               continue

           this_time = timestr2flt(m['new_file'][0:12]+'00.00')

           this_file = m['new_file'][13:]

           if this_file in self.last_radar_received:
               last_time = self.last_radar_received[this_file]

               if  (this_time - last_time) > self.product_interval :
                   logger.error( f"missed {this_file} between {timeflt2str(last_time)} and {m['new_file']}" )

           else:
               self.last_radar_received[this_time] = this_time

