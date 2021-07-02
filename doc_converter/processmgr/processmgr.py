""" Module for passing data to and from api and libreoffice subprocesses on the server """
import os, sys, uuid, time, re, pickle, subprocess, logging
from fastapi import UploadFile
from doc_converter.processmgr.redis_wrapper import RedisWrapper
from doc_converter.processmgr.uno_controller import UnoConverter
from doc_converter.util import TEMP_FOLDER

logger = logging.getLogger(__name__)


class ProcessMgr(object):
    """ 
    Container class for managing interface between api and worker subprocesses
    
    Arguments:
        in_filepath {str} -- file to be convertered
        convert_type {ProcessMgr.convert_types} -- file type to convert to. Is a process_mgr.convert_types object
            note: only convert_types.SVG is supported now
        out_dir {str} -- (Optional) file path to directory where converted file should end up
            after libreoffice runs its conversion
        blob_name {str} -- (Optional) name of the blob where the converted file should be stored    
    
    """
    @staticmethod
    def get_file_extension(filepath):
        """ Gets a file extension from a filepath """
        return filepath.rsplit('.', 1)[1].lower()

    @staticmethod
    def get_filename(filepath):
        """ Gets a file name from a file path """
        return os.path.basename(filepath).rsplit('.', 1)[0]

    ALLOWED_EXTENSIONS = ['ppt', 'pptx', 'doc', 'docx', 'xls', 'xlsx', 'odt', 'ods', 'odp', 'odg']
    TIMEOUT_TIME = 10 # secs
    EXPIRY_TIME = 3600 # secs

    @staticmethod
    def allowed_file(filename):
        """ Determines filetypes from extension and whether it can be converted """
        return '.' in filename and ProcessMgr.get_file_extension(filename) in ProcessMgr.ALLOWED_EXTENSIONS

    class ConvertTypes:
        "Conversion type options for processmgr"
        SVG = "svg"
        PNG = "png"
        JPG = "jpg"


    guid_regex = re.compile(r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}')

    @staticmethod
    def extract_guid(input_string):
        matches = ProcessMgr.guid_regex.findall(input_string)
        if len(matches) > 0:
            return matches[0]
        else:
            return None



    def __init__(self, file: bytes, filename: str, convert_type: str):

        self.file = file
        self.convert_type = convert_type
        self.file_extension = ProcessMgr.get_file_extension(filename)
        self.redis_key = self.extract_guid(filename) or str(uuid.uuid4())
        self.temp_filename = os.path.join(TEMP_FOLDER, self.redis_key + "." + self.file_extension)
        self.converted = False

    
    """ Maps file extensions to filter data """
    extension_map = {
        "ppt" : ["powerpoint", "impress"],
        "pptx" : ["powerpoint", "impress"],
        "doc" : ["word", "writer"],
        "docx" : ["word", "writer"],
        "xls" : ["excel", "calc"],
        "xlsx" : ["excel", "calc"],
        "odt" : ["word", "writer"],
        "ods" : ["excel", "calc"],
        "odp" : ["powerpoint", "impress"],
        "odg" : ["visio", "draw"]
    }
    
    def create_outfile_name(self):
        """Generates the filename of the returned file after
        libreoffice has completed file conversion
        
        Returns:
            string -- file path to converted file (assuming file has been converted)
        """

        self.outfile = os.path.join(TEMP_FOLDER, self.redis_key + "." + self.convert_type)
        return self.outfile

    def convert(self):
        """ Converts a file using the libreoffice command line interface.  The converted filename is output. """
        try:
            self.prep_conversion()
            converter = UnoConverter(input_dir=TEMP_FOLDER, output_dir=TEMP_FOLDER)
            converter.convert(self.temp_filename, self.convert_type)
            if os.path.exists(self.outfile):
                self.converted = True
                self.cache()
                self.teardown()
                return self.outfile
            else:
                raise IOError("Document conversion failed")
        except Exception as ex:
            logger.exception(ex)
            raise IOError("Document conversion failed")

    def serialize(self):
        return pickle.dumps(self)
    
    @classmethod
    def deserailize(cls, pickle_data: bytes):
        return pickle.loads(pickle_data)

    def prep_conversion(self):
        self.create_outfile_name()
        self.teardown()
        with open(self.temp_filename, 'wb+') as f:
            f.write(self.file)
        

    def teardown(self):
        try:
            os.remove(self.temp_filename)
        except Exception:
            pass
        try:
            os.remove(self.outfile)
        except Exception:
            pass
        if self.converted:
            r = RedisWrapper.get_redis()
            r._redis.delete(self.redis_key)

    def cache(self):
        r = RedisWrapper.get_redis()
        r.store(self.outfile, self.get_converted_file_key())

    @classmethod
    def from_upload_file(cls, file: UploadFile, convert_type: str):
        return cls(file.file.read(), file.filename, convert_type)

    def handoff_to_worker(self):
        from doc_converter.celery import convert_task
        r = RedisWrapper.get_redis()
        r._redis.set(self.redis_key, self.serialize())
        convert_task.delay(self.redis_key)

    def reserve_cache_key(self):
        r = RedisWrapper.get_redis()
        r._redis.set(self.get_converted_file_key(), b'\x00')

    def get_converted_file_key(self):
        return self.convert_type + "-" + self.redis_key


        


