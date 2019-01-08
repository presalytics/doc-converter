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

    def __init__(self, in_filepath, convert_type, out_filepath=None)
        self.in_filepath = in_filepath
        self.convert_type = convert_type
        self.file_extension = get_file_extension(in_filepath)
        if out_filepath is None:
            self.out_filepath = os.path.dirname(in_filepath)
        else:
            self.out_filepath = out_filepath

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

    @staticmethod
    def get_file_extension(filepath):
        return filepath.split('.').last()

    def build_filter(self):
        


    def convert(self):
        command = "soffice --headless --invisible --convert-to:{}".format(self.convert_type.value, )
    



