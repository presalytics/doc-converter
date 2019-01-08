""" Module for passing data to and from api and libreoffice subprocesses on the server """
import subprocess
import os
from enum import Enum


ALLOWED_EXTENSIONS = ['ppt', 'pptx', 'doc', 'docx', 'xls', 'xlsx', 'odt', 'ods', 'odp', 'odg']

def allowed_file(filename):
    """ Determines filetypes from extension and whether it can be converted """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class processmgr:

<<<<<<< HEAD
    @staticmethod
    def get_file_extension(filepath):
        return filepath.rsplit('.', 1)[1].lower()
    
    @staticmethod 
    def get_filename(filepath):
        return os.path.basename(filepath).rsplit('.', 1)[0]

    def __init__(self, in_filepath, convert_type, out_dir=None):
        self.in_filepath = in_filepath
        self.convert_type = convert_type
        self.file_extension = processmgr.get_file_extension(in_filepath)
        if out_dir is None:
            self.out_dir = os.path.dirname(in_filepath)
        else:
            self.out_dir = out_dir
        self.build_filter()
        self.converted = False
        

=======
    def __init__(self, in_filepath, convert_type, out_filepath=None)
        self.in_filepath = in_filepath
        self.convert_type = convert_type
        self.file_extension = get_file_extension(in_filepath)
        if out_filepath is None:
            self.out_filepath = os.path.dirname(in_filepath)
        else:
            self.out_filepath = out_filepath
>>>>>>> fab8f2e60c26beea7e4ea76e42c2377d72c1ccb3

    class convert_types(Enum):
        SVG = "svg"
        PNG = "png"
        JPG = "jpg"
    
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
        "odt" : ["visio", "draw"]
    }

<<<<<<< HEAD

    def build_filter(self):
        program = processmgr.extension_map[self.convert_type][1]
        export = "{}_{}_Export".format(program, self.convert_type.value)
        self.filter = export
=======
    @staticmethod
    def get_file_extension(filepath):
        return filepath.split('.').last()

    def build_filter(self):
>>>>>>> fab8f2e60c26beea7e4ea76e42c2377d72c1ccb3
        


    def convert(self):
<<<<<<< HEAD
        command = "soffice --headless --invisible --convert-to:{}".format(
            self.convert_type.value,
            self.
            teste get_file_extension
            
        
        )
        exit_code = subprocess.call(command)
        if exit_code == 0:
            self.outfile = os.path.join(self.out_dir, processmgr.get_filename(self.in_filepath) + '.' + self.convert_type.value)
            if os.path.exists(self.outfile):
                self.converted = True
                return self.outfile
            else:
                raise Exception("Conversion of {} to {} failed.  Check file format.".format(self.in_filepath, self.convert_type.name))
        else:
            raise Exception("Conversion process exited with code {}.  Likely File Error.  check for corrupeted input file.".format(exit_code))
=======
        command = "soffice --headless --invisible --convert-to:{}".format(self.convert_type.value, )
    
>>>>>>> fab8f2e60c26beea7e4ea76e42c2377d72c1ccb3



