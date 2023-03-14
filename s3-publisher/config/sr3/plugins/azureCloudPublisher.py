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
from urllib.parse import urlparse
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)

class AzureCloudPublisher(FlowCB):
    """Azure cloud data publisher"""

    def __init__(self, options):
        """Initialize plugin and check environment variables"""

        self.o = options

        self.container_name = os.environ.get('AZURE_CONTAINER_NAME', None)
        self.connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING', None)
        
        if None in [self.container_name, self.connection_string]:
            raise EnvironmentError('Environment variables not set or accessible')

        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string)
        except Exception as err:
            logger.error("Failed to initialize connection to container with connection string")
            logger.error(err)
            raise err

    def after_accept(self, worklist) -> None:
        """
        sarracenia dispatcher

        :param worklist: `sarracenia.flowcb`
        :returns: None 
   
        """

        new_incoming=[]

        # Send each message which was properly downloaded or worked on
        for msg in worklist.incoming:
           try:
               # Filepath of the local file
               filepath = os.sep + msg['relPath'] 
               logger.debug('Local filepath: {}'.format(filepath))
               
               self.publish_to_azure(msg=msg, filepath=filepath)

               # If pulbish was successful, append to new worklist.incoming
               new_incoming.append(msg)

           except Exception as err:
               # Publish was not successful, append to worklist.failed for retry
               logger.error("Error sending to remote")
               logger.error(err)
               worklist.failed.append(msg)
               continue

        worklist.incoming = new_incoming


    def publish_to_azure(self, msg, filepath: str) -> bool:
        """
        Azure blob file publisher

        :param filepath: `str` of local filepath to upload

        :returns: `bool` of dispatch result
        """
        
        # Remove leading /'s from filepath to allow proper dir creation on azure
        remote_filepath = filepath.lstrip("/")

        # Set blob name to the relative path within the container
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=remote_filepath)

        with open(filepath, 'rb') as data:
            result = blob_client.upload_blob(data=data, overwrite=True)
            logger.debug(result)
            logger.info('Published file to {}'.format(blob_client.url))
            p_url = urlparse(blob_client.url)
            # Overwrite where to retreive the file in posted messages
            msg["new_baseUrl"] = '{uri.scheme}://{uri.netloc}/'.format(uri=p_url)
            msg["new_retPath"] = blob_client.container_name + "/" + blob_client.blob_name

        return True

    def __repr__(self):
        return '<AzureCloudPublisher>'
