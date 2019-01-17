""" Module for passing data to and from api and libreoffice subprocesses on the server """
from subprocess import Popen, PIPE
import os, sys, uuid

class processmgr:
    """ Container class for managing interface between flask and libreoffice subprocesses """
    @staticmethod
    def get_file_extension(filepath):
        """ Gets a file extension from a filepath """
        return filepath.rsplit('.', 1)[1].lower()

    @staticmethod
    def get_filename(filepath):
        """ Gets a file name from a file path """
        return os.path.basename(filepath).rsplit('.', 1)[0]

    ALLOWED_EXTENSIONS = ['ppt', 'pptx', 'doc', 'docx', 'xls', 'xlsx', 'odt', 'ods', 'odp', 'odg']

    @staticmethod
    def allowed_file(filename):
        """ Determines filetypes from extension and whether it can be converted """
        return '.' in filename and processmgr.get_file_extension(filename) in processmgr.ALLOWED_EXTENSIONS

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
        self.outfile = None
        self.command = self.build_command()
        self.create_outfile_name()

    

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


    def build_filter(self):
        """ builds the libreoffice 'filter' for commmand line file conversion """
        program = processmgr.extension_map[self.file_extension][1]
        export = "{}_{}_Export".format(program, self.convert_type)
        self.filter = export
    
    def build_command(self):
        command = [
            "soffice",
            "--headless",
            "--invisible",
            "--convert-to",
            "{}:{}".format(self.convert_type, self.filter),
            self.in_filepath,
            "--outdir",
            self.out_dir
        ]
        # commentted out command obsolete, should work with subprocess.call where shell=True (security risk)
        # command = "soffice --headless --invisible --convert-to {}:{} {} --outdir {}".format(
        #     self.convert_type,
        #     self.filter,
        #     self.in_filepath,
        #     self.out_dir
        # )
        return command

    def check_command(self):
        return self.command
    
    def create_outfile_name(self):
        self.outfile = os.path.join(self.out_dir, processmgr.get_filename(self.in_filepath) + '.' + self.convert_type)
        return self.outfile

    def convert(self):
        """ Converts a file using the libreoffice command line interface.  The converted filename is output. """
        self.create_outfile_name()
        try:
            os.remove(self.outfile)
        except:
            pass
        p = Popen(self.command, stdout=PIPE, stderr=PIPE, bufsize=-1, close_fds=True)
        output, err = p.communicate()
        rc = p.returncode
        if rc == 0:
            if os.path.exists(self.outfile):
                self.converted = True
                return self.outfile
            else:
                raise IOError("Document conversion failed")
                # raise IOError([
                #     "Conversion of {} to {} failed.  Check file format.".format(self.in_filepath, self.convert_type),
                #     "exit code: {}".format(rc),
                #     "stdout: {}".format(str(output, 'utf-8')),
                #     "stderr: {}".format(str(err, 'utf-8')) #last line of thrown exception
                # ])
        else:
            raise IOError("Conversion process exited with code {}.  Likely File Error.  Check for corrupted input file.".format(rc))