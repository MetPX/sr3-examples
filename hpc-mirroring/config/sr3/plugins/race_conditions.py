#!/usr/bin/python3

import itertools
import logging

import os

from sarracenia.flowcb import FlowCB
from sarracenia import timestr2flt, timeflt2str, nowflt, naturalSize
import time

logger = logging.getLogger(__name__)


class Race_conditions(FlowCB):
    """
       look at a stream of published paths for multiple different operations on the same file.
       if a file gets multiple modifications, that's ignored, it is only different operations... modify+rename, link+mkdir etc...
       where the order of operations can lead to different results depending on order of execution.

       If the operations are too close together (time_interval_threshold), then print a warning.


       usage in a subscriber config:

       race_conditions_time_interval_threshold 2
       callback race_conditions

       baseDir /hoho/sourcedir
       post_baseDir /hoho/destdir

    """
    def __init__(self, options):

        super().__init__(options,logger)
        self.o.add_option('race_conditions_time_interval_threshold', 'duration', 5)
        self.o.add_option('race_conditions_compare_against', 'str', None)

        self.tallies={}

    def clean_tallies(self):
        logger.info( f"" )

        # rebuild tallies, cleaning out old entries based on pubTimes.
        min_time= timeflt2str(time.time()-300)
        new_tallies={}
        for p in self.tallies:
            for op in self.tallies[p]:
                new_op=[]
                for t in self.tallies[p][op]:
                    if t > min_time:
                        new_op.append(t)
                if len(new_op) > 0: 
                    if not p in new_tallies:
                        new_tallies[p] = {}
                    new_tallies[p][op] = new_op
             
        
        self.tallies = new_tallies
        logger.info( f" tallies left: {len(self.tallies)} " )
        pass

    def on_housekeeping(self):

        logger.info( f" tallies before cleaning: {len(self.tallies)} " )
        for p in self.tallies:
            if not (('JOBID' in self.tallies[p] and len(self.tallies[p]) > 2) or (len(self.tallies[p]) > 1)):
                continue

            # assert: there is more than one different op in this tally.

            #remove jobid for later.
            if 'JOBID' in self.tallies[p]:
                jobid=self.tallies[p]['JOBID']
                del self.tallies[p]['JOBID']
            else:
                jobid="n/a"
            # find the total difference of time among all the operations.

            times = list(map( timestr2flt, list(itertools.chain( *self.tallies[p].values()))))
            diffs = [abs(e[1] - e[0]) for e in itertools.pairwise(times)]
            total_diff=sum(diffs)
            #logger.info( f" {times=}, {diffs=}, {total_diff=}" )

            if total_diff < self.o.race_conditions_time_interval_threshold:
                dest_path = '/' + p
                source_path = source_path.replace(self.o.post_baseDir,self.o.baseDir)
                difference_found=False
                if os.path.exists(source_path):
                    if os.path.exists(dest_path):
                        source_stat = os.stat( '/' +p)
                        dest_stat = os.stat( dest_path.replace(self.o.post_baseDir, self.o.baseDir))
                        if source_stat.st_size == dest_stat.st_size:
                            sz="same size on both site stores"
                        else:
                            sz="file differente on each side"
                            difference_found=True
                    else:
                        sz="file missing on destination"
                        difference_found=True
                else: #except:
                    if os.path.exists(dest_path):
                        sz="file missing on source"
                        difference_found=True
                    else:
                        sz="file gone, cannot compare"
                        difference_found=False

                if difference_found:
                    logger.error( f" CORRUPTION. job: {jobid}, ops within {total_diff:5.3g} seconds on: {p} ({sz}): {self.tallies[p]}" )
                else:
                    logger.warning( f" job: {jobid}, ops within {total_diff:5.3g} seconds on: {p} ({sz}): {self.tallies[p]}" )
            #else:
            #    logger.info( f"multiple operations in job: {jobid} total time difference: {total_diff:5.3g} ... on {p} ({sz}): {self.tallies[p]}" )
            
        self.clean_tallies()


    def tally(self,m):

        relPath=m['relPath']
        op='modify'
        if 'fileOp' in m:
            ops=list(m['fileOp'].keys())
            if len(ops) == 1:
                op=ops[0]
            elif 'link' and 'rename' in ops:
                op='link'
            elif 'directory' and 'remove' in ops:
                op='rmdir'
            else:
                logger.error( f"ignoring... do not know what to do with {m['relPath']} filop {m['fileOp']}")
                

        if not relPath in self.tallies:
            self.tallies[ relPath ] = {}

        if op not in self.tallies[relPath]:
            self.tallies[relPath][op] = []

        self.tallies[relPath][op].append( m['pubTime'] )
        if 'JOBID' in m:
            if not 'JOBID' in self.tallies[relPath]:
                self.tallies[relPath]['JOBID']= set([])
            self.tallies.relPath['JOBID'] |= m['JOBID']


    def after_accept(self, worklist):

        this_batch=len(worklist.incoming)
        if this_batch < 1:
            return

        new_incoming=[]
        for m in worklist.incoming:
            if not 'relPath' in m:
                continue
            self.tally(m)
