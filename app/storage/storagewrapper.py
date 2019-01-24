""" Wrapper class for communicating with azure blob storage """

import os, uuid
from environs import Env
from azure.storage.blob import BlockBlobService

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
        self.service = BlockBlobService(
            account_name=os.environ['Azure__AccountName'], 
            account_key=os.environ['Azure__AccountKey']
        )
        self.container_name = os.environ['Azure__BlobContainers__Svg']
        self.service.create_container(container_name=self.container_name)
        self.blob_placeholder = "Temp data -- Msg: This blob is allocated, but unused"

    def allocate_blob(self):
        """
        Reserves a blob with a few bytes of temporary data.
        Allows fast return of blob metadata and permits async/post-process operations
        on the doc_converter microservice.          
        
        Returns: a blob name string generated via uuid

        """
        blob_name = "svg-" + str(uuid.uuid4())
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
        
        Returns: status_code (integer value)
            status_code: 0 = operation successful
            status_code: 1 = operation failed
            function raises error on failed operations,
            so status 1 code path should not be reached.
            a return of status_code=1 means mean function failed outside
            of designed code path.

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
        




