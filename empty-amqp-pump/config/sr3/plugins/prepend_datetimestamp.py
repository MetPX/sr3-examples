import datetime
import logging
import paramiko
import re
import sarracenia
from sarracenia.flowcb import FlowCB
import time
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class Prepend_datetimestamp(FlowCB):

    def after_accept(self, worklist):

        for m in worklist.incoming:
            file_name = m['new_file']
            yyyymmddHHMMSS = time.strftime("%Y%m%d%H%M%S", time.gmtime())
            m['new_file'] = yyyymmddHHMMSS + '_' + file_name
