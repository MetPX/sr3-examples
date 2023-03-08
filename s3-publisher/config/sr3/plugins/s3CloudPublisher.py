# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>, Tyson Kaufmann
#
# Copyright (c) 2021 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================



import logging
import os
from sarracenia.flowcb import FlowCB
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class S3CloudPublisher(FlowCB):
    """Cloud data publisher for s3"""

    def __init__(self, options):
        """initialize"""

        self.o = options

        self.s3_url = os.environ.get('S3_URL', None)
        self.s3_bucket_name = os.environ.get('S3_BUCKET_NAME', None)
        aws_id = os.environ.get('AWS_ACCESS_KEY_ID', None)
        aws_key = os.environ.get('AWS_SECRET_ACCESS_KEY', None)
        aws_region = os.environ.get('AWS_REGION', None)

        if None in [self.s3_url, self.s3_bucket_name, aws_id, aws_key]:
            raise EnvironmentError('environment variables not set')

        # Connect to a specific region if specified
        if aws_region:
            self.s3_client = boto3.client('s3', endpoint_url=self.s3_url, 
                    aws_access_key_id=aws_id, aws_secret_access_key=aws_key,
                    region_name=aws_region)
        else:
            self.s3_client = boto3.client('s3', endpoint_url=self.s3_url, 
                    aws_access_key_id=aws_id, aws_secret_access_key=aws_key)

    def after_accept(self, worklist) -> None:
        """
        sarracenia dispatcher

        :param worklist: `sarracenia.flowcb`
        :returns: None 
   
        """

        new_incoming=[]

        for msg in worklist.incoming:
           try:
               # Filepath of the local file
               filepath = os.sep + msg['relPath']
               logger.debug('Local filepath: {}'.format(filepath))

               identifier = os.path.basename(filepath)

               self.publish_to_s3(msg=msg, filepath=filepath)

               # If pulbish was successful, append to new worklist.incoming
               new_incoming.append(msg)

           except Exception as err:
               # Publish was not successful, append to worklist.failed for retry
               logger.error("Error sending to remote")
               logger.error(err)
               worklist.failed.append(msg)
               continue

        worklist.incoming = new_incoming


    def publish_to_s3(self, msg, filepath: str) -> None:
        """
        s3 object publisher

        :param filepath: `str` of local filepath to upload

        :returns: `bool` of dispatch result
        """

        remote_filepath = filepath.lstrip("/")

        url = os.path.normpath(os.path.join(
             self.s3_client.meta.endpoint_url, self.s3_bucket_name, remote_filepath))

        with open(filepath, 'rb') as data:
            self.s3_client.upload_fileobj(data, self.s3_bucket_name, remote_filepath)
            logger.info('Published file to {}'.format(url))
            # Rename message parameters to set new location as the bucket
            msg["new_baseUrl"] = self.s3_client.meta.endpoint_url
            msg["new_retPath"] = self.s3_bucket_name + "/" + remote_filepath

    def __repr__(self):
        return '<S3CloudPublisher>'
