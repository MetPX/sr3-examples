# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
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
    """core cloud data publisher"""

    def __init__(self, options):
        """initialize"""

        self.o = options

        self.container_name = os.environ.get('AZURE_CONTAINER_NAME', None)
        self.connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING', None)
        
        if None in [self.container_name, self.connection_string]:
            raise EnvironmentError('environment variables not set')

        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string)
        except ValueError as err:
            logger.error("Failed to initialize connection to container with connection string")
            logger.error(err)
            raise err

    def after_work(self, worklist) -> None:
        """
        sarracenia dispatcher

        :param worklist: `sarracenia.flowcb`
        :returns: None 
   
        """

        for msg in worklist.ok:
           try:
               filepath = msg['new_dir'] + os.sep + msg['new_file']
               logger.info('Filepath: {}'.format(filepath))
               identifier = msg['new_file']

               self.publish_to_azure(msg=msg, blob_identifier=identifier, filepath=filepath)

               logger.debug('not checking return status is odd, do we want retry-logic?')

           except Exception as err:
               print("ERROR", err)
               logger.warning(err)


    def publish_to_azure(self, msg, blob_identifier: str, filepath: str) -> bool:
        """
        Azure blob file publisher

        :param blob_identifier: `str` of blob id
        :param filepath: `str` of local filepath to upload

        :returns: `bool` of dispatch result
        """

        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=blob_identifier)

        try:
            with open(filepath, 'rb') as data:
                result = blob_client.upload_blob(data)
                logger.info(result)
                logger.info('published to {}'.format(blob_client.url))
                p_url = urlparse(blob_client.url)
                msg["baseUrl"] = '{uri.scheme}://{uri.netloc}/'.format(uri=p_url)
                msg["retPath"] = blob_client.container_name + "/" + blob_client.blob_name
        except ResourceNotFoundError as err:
            logger.error(err)
            return False

        return True

    def __repr__(self):
        return '<AzureCloudPublisher>'
