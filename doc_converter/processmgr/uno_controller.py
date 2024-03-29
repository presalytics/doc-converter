# pyright: reportMissingImports=false, reportUnusedVariable=warning, reportUntypedBaseClass=error, reportUntypedBaseClass=false
import os
import logging
import time
import subprocess
import psutil


logger = logging.getLogger(__name__)


try:
    # python3 must be running as root ("sudo python3") in order to bind to soffice.bin proces.
    # otherwiese import uno will fail as 'Cannot import Element'
    # to simplify, always debug this module inside a built docker container
    import uno  # noqa: F401
    import unohelper  # noqa: F401
    import pyuno  # noqa: F401

    from unotools import Socket, connect
    from unotools.component.calc import Calc
    from unotools.component.writer import Writer
    from unotools.unohelper import convert_path_to_url
    from unotools.unohelper import LoadingComponentBase
except (ImportError, ModuleNotFoundError):
    msg = """

    -------------------------------------------------------------
    Uno apis are unavailable.

    Application is running in API-only mode.

    Any attempt at document conversion on this process will fail.
    Please ensure a companion worker process is running before
    doing any document conversion
    -------------------------------------------------------------
    """
    logger.info(msg)

    class LoadingComponentBase(object):  # type: ignore
        """Dummy class"""
        pass


class Impress(LoadingComponentBase):
    URL = 'private:factory/simpress'


class UnoConverter(object):
    def __init__(self, input_dir=None, output_dir=None):
        self.start_soffice()
        self.context = connect(Socket("localhost", "8100"))
        self.output_dir = output_dir
        if self.output_dir is None:
            self.output_dir = os.getcwd()
        self.input_dir = input_dir
        if self.input_dir is None:
            self.input_dir = os.getcwd()

    DEAD_STATUSES = (
        psutil.STATUS_DEAD,
        psutil.STATUS_ZOMBIE
    )

    def start_soffice(self):
        if "soffice.bin" not in (p.name() for p in psutil.process_iter() if p.status() not in self.DEAD_STATUSES):
            subprocess.Popen('libreoffice --accept="socket,host=localhost,port=8100;urp;StarOffice.Service" --norestore --nologo --headless --nodefault -env:UserInstallation=file:///tmp/libreoffice',
                             stdin=None,
                             stdout=None,
                             stderr=None,
                             close_fds=True,
                             shell=True
                             )
            time.sleep(1)

    def kill_soffice(self):
        for p in psutil.process_iter():
            if p.name() == 'soffice.bin' or p.name() == 'oosplash':
                try:
                    if p.status() == psutil.STATUS_ZOMBIE:
                        p.wait()
                    elif p.is_running():
                        p.kill()

                except psutil.ZombieProcess:
                    p.wait()

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
        self.wait_for_completion(out_filename)
        return out_filename

    def wait_for_completion(self, out_filename):
        occupied = True
        while occupied:
            occupied = self.has_handle(out_filename)
            if occupied:
                time.sleep(0.1)

    def has_handle(self, fpath):
        for proc in psutil.process_iter():
            try:
                for item in proc.open_files():
                    if fpath == item.path:
                        return True
            except Exception:
                pass

        return False

    COMPONENT_MAP = {
        "Writer": {
            "file_extensions": [
                "doc",
                "docx",
                "odt",
                "docm"
            ],
            "export_options": {
                "pdf": "writer_pdf_Export",
                "html": "HTML (StarWriter)",
                "docx": "Office Open XML Text Document"
            }
        },
        "Calc": {
            "file_extensions": [
                "ods",
                "xlsx",
                "xls",
                "xlsb",
                "xlsm",
                "csv"
            ],
            "export_options": {
                "pdf": "calc_pdf_Export",
                "html": "HTML (StarCalc)",
                "xlsx": "Office Open XML Spreadsheet"
            }
        },
        "Impress": {
            "file_extensions": [
                "ppt",
                "pptx",
                "odp"
            ],
            "export_options": {
                "pdf": "impress_pdf_Export",
                "pptx": "Office Open XML Presentation",
                "svg": "impress_svg_Export",
                "png": "draw_png_Export"
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
