import unittest, os
from doc_converter.spooler.spooler import svg_convert

class SpoolerTest(unittest.TestCase):
    def setup(self):
        self.rectangle_path = os.path.join(os.path.dirname(os.path.abspath()), "files", "Rectangle.pptx")
        try:
            os.system('soffice --accept="socket,host=localhost,port=8100;urp;StarOffice.Service"')
        except:
            pass

    def spooler_test(self):
        pass