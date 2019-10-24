import os, logging, sys
from os.path import basename, join as pathjoin, splitext
from subprocess import Popen
import psutil
# python3 must be running as root ("sudo python3") in order to bind to soffice.bin proces.
# otherwiese import uno will fail as 'Cannot import Element'
import uno
import unohelper
import pyuno
import unotools


from unotools import Socket, connect
from unotools.component.calc import Calc
from unotools.component.writer import Writer
from unotools.unohelper import convert_path_to_url
from unotools.unohelper import LoadingComponentBase

logger = logging.getLogger('doc_converter.uno_controller')

        
class Impress(LoadingComponentBase):
    URL = 'private:factory/simpress'

class UnoConverter(object):
    def __init__(self, input_dir=None, output_dir=None):
        if not "soffice.bin" in (p.name() for p in psutil.process_iter()):
            Popen('libreoffice --accept="socket,host=localhost,port=8100;urp;StarOffice.Service" --norestore --nologo --nodefault --headless -env:UserInstallation=file:///tmp/libreoffice',
                stdin=None, 
                stdout=None, 
                stderr=None, 
                close_fds=True
            )
        self.context = connect(Socket("localhost", "8100"))
        self.output_dir = output_dir
        if self.output_dir is None:
            self.output_dir = os.getcwd()
        self.input_dir = input_dir
        if self.input_dir is None:
            self.input_dir = os.getcwd()
            
        
    def get_component(self, filepath, context):
        file_url = convert_path_to_url(filepath)
        component_data = UnoConverter.get_component_data_from_filename(file_url)
        name = component_data[0]
        if name == "Calc":
            component = Calc(context, file_url)
        elif name == "Writer":
            component = Writer(context, file_url)
        elif name == "Impress":
            component = Impress(context, file_url)            
        else:
            raise ValueError('Unsupported file type.')
        return component


    def convert(self, filename, new_extension):
        filepath = os.path.join(self.input_dir, filename)
        component = self.get_component(filepath, self.context)
        export_options = self.__class__.COMPONENT_MAP[component.__class__.__name__]["export_options"]
        export_filter = export_options[new_extension]
        if export_filter is None:
            raise ValueError('Unsupported conversion request.')
        out_filename = os.path.join(self.output_dir, filename.rsplit('.')[0] + '.' + new_extension)
        out_url = convert_path_to_url(out_filename)
        component.store_to_url(out_url, 'FilterName', export_filter)
        component.close(True)
        return out_filename

    COMPONENT_MAP = {
        "Writer" : {
            "file_extensions" :[
                "doc",
                "docx",
                "odt",
                "docm"
            ],
            "export_options" : {
                "pdf": "writer_pdf_Export",
                "html": "HTML (StarWriter)",
                "docx" : "Office Open XML Text Document"
            }
        },
                
        "Calc" : {
            "file_extensions" : [
                "ods",
                "xlsx",
                "xls",
                "xlsb",
                "xlsm",
                "csv"
            ],
            "export_options" : {
                "pdf" : "calc_pdf_Export",
                "html" : "HTML (StarCalc)",
                "xlsx" : "Office Open XML Spreadsheet"
            }
        },
        "Impress" : {
            "file_extensions" : [
                "ppt",
                "pptx",
                "odp"
            ],
            "export_options" : {
                "pdf" : "impress_pdf_Export",
                "pptx" : "Office Open XML Presentation",
                "svg" : "impress_svg_Export",
                "png" : "draw_png_Export"
            }
        }
    }

    @classmethod
    def get_component_data_from_filename(cls, filepath):
        extension = filepath.rsplit('.', 1)[1].lower()
        for key, val in cls.COMPONENT_MAP.items():
            if extension in val["file_extensions"]:
                component_data = (key, val,)
        return component_data