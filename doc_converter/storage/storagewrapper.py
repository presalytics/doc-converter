""" Wrapper class for communicating with azure blob storage """

import os, uuid, logging
from environs import Env
from azure.storage.blob import BlockBlobService

logger = logging.getLogger('doc_converter.blobber')


env = Env()
env.read_env()


class Blobber():
    """ 
    Wrapper class for azure blob service

    Class initialization reads azure connection information
    from environment variables and logs into the azure storage account
    environment varialbes are automatically populated from .env file 
    in project root via the environs package.

    Init then creates/accesses container for the service.
    """
    def __init__(self):
        try:
        # if "Azure__BlobEndpoint" in os.environ:
        #     AZURE_DOMAIN =  os.environ['Azure__BlobEndpoint']
        # else:
        #     AZURE_DOMAIN = None
        # protocol = "https"
        # if env.bool("Azure__IsEmulated"):
        #     protocol = "http"
        # self.service = BlockBlobService(
        #     account_name=os.environ['Azure__AccountName'], 
        #     account_key=os.environ['Azure__AccountKey'],
        #     custom_domain=AZURE_DOMAIN,
        #     protocol=protocol
        # )
            self.build_azure_connection_string()
            self.service = BlockBlobService(connection_string=self.connection_string)
            self.container_name = os.environ['Azure__BlobContainers__Svgs']
            self.service.create_container(
                container_name=self.container_name,
                fail_on_exist=False
            )
            self.blob_placeholder = "Temp data -- Msg: This blob is allocated, but unused"
        except Exception as err:
            logger.info("Blob connection failed with connection string: {}".format(self.connection_string))
            logger.error(err)

    def build_azure_connection_string(self):
        protocol = "DefaultEndpointsProtocol=https;"
        if env.bool("Azure__IsEmulated", False):
            protocol = "DefaultEndpointsProtocol=https;"
        account_name = "AccountName={};".format(os.environ['Azure__AccountName'])
        account_key = "AccountKey={};".format(os.environ['Azure__AccountKey'])
        blob_endpoint = "BlobEndpoint=https://{};".format(os.environ['Azure__BlobEndpoint'])
        self.connection_string = protocol + account_name + account_key + blob_endpoint


    def allocate_blob(self, blob_name = None):
        """
        Reserves a blob with a few bytes of temporary data.
        Allows fast return of blob metadata and permits async/post-process operations
        on the doc_converter microservice.          
        
        Returns: a blob name string generated via uuid

        """
        if not blob_name:
            _id = str(uuid.uuid4())
            blob_name = "svg-" + _id
        self.service.create_blob_from_text(
            container_name=self.container_name,
            blob_name=blob_name,
            text=self.blob_placeholder
            )
        return blob_name
    
    def get_blob_uri(self, blob_name):
        """
        Generates a uri for an existing blob

        Returns: a Uri for a blob (string format)

        Param: blob_name: name of that that needs a uri
        """
        return self.service.make_blob_url(
            container_name=self.container_name,
            blob_name=blob_name
        )

    def put_blob(self, blob_name, filepath):
        """
        Rewrites file at blob with blob_name to to file at file_path.
        
        If no blob with blob_name is allocated, then method creates
        new blob in container with blob_name and uploads file

        Param: blob_name: name of existing blob or blob to be created

        Param: filepath: local file location of file to uploaded 
            to azure blob(do not use urls)
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError("File not found: {}".format(filepath))
        self.service.create_blob_from_path(
            container_name=self.container_name,
            blob_name=blob_name,
            file_path=filepath
        )
        




