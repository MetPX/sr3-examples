#!/usr/bin/python3

import logging

from sarracenia.flowcb import FlowCB
from sarracenia import timestr2flt, nowflt, naturalSize

logger = logging.getLogger(__name__)


class Tally_volume(FlowCB):
    """
    """
    def __init__(self, options):

        super().__init__(options,logger)

        self.tallies = { 'bytes': 0, 'files': 0 }


    def on_housekeeping(self):

        logger.info( f" files: bytes: {self.tallies['bytes']} files {self.tallies['files']}"  )
        self.tallies = { 'bytes': 0, 'files': 0 }

    def after_accept(self, worklist):

        this_batch=len(worklist.incoming)
        if this_batch < 1:
            return

        new_incoming=[]
        for m in worklist.incoming:
             if 'size' in m:
                 self.tallies['bytes']  += m['size']
                 self.tallies['files']  += 1

        return
        if self.tallies['files'] > 0:
            logger.info( f"after a batch of {this_batch} files: bytes: {naturalSize(self.tallies['bytes'])} "\
                    f"count: {self.tallies['files']} mean: "\
                    f"{naturalSize(self.tallies['bytes']/self.tallies['files'])}"  )
