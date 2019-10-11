import os, logging, sys
from os.path import basename, join as pathjoin, splitext
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

logger = logging.getLogger('uno_controller')

class Impress(LoadingComponentBase):
    URL = 'private:factory/simpress'

class UnoConverter(object):
    def __init__(self):
        if not "soffice.bin" in (p.name() for p in psutil.process_iter()):
            os.system('soffice --accept="socket,host=localhost,port=8100;urp;StarOffice.Service" --norestore --nologo --nodefault --headless')
        
        # initialize uno desktop
        
    def get_component(self, args, context):
        _, ext = splitext(args.file_)
        url = convert_path_to_url(args.file_)
        if ext == '.odt':
            component = Writer(context, url)
        elif ext == '.ods':
            component = Calc(context, url)
        else:
            raise ValueError('Supported file type are [odt|ods]: {}'.format(ext))
        return component


    def convert_pdf(self, args, context):
        component = self.get_component(args, context)
        filename = basename(args.file_).split('.')[0] + '.pdf'
        url = convert_path_to_url(pathjoin(args.outputdir, filename))
        property_ = '{}_pdf_Export'.format(component.__class__.__name__.lower())
        component.store_to_url(url, 'FilterName', property_)
        component.close(True)