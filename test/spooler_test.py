import unittest, os, shutil, sys
top_level = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, top_level)
import doc_converter
import doc_converter.common.util

class SpoolerTest(unittest.TestCase):
    def setup(self):
        self.rectangle_path = os.path.join(os.path.dirname(os.path.abspath()), "files", "Rectangle.pptx")
        try:
            os.system('soffice --accept="socket,host=localhost,port=8100;urp;StarOffice.Service"')
        except:
            pass

    def test_script_scripts(self):
        test_file = os.path.join(os.path.dirname(__file__), "files", "test-img.svg")
        tmp_file = os.path.join(os.path.dirname(__file__), "files", "test-img.svg.tmp")
        shutil.copyfile(test_file, tmp_file)
        doc_converter.common.util.strip_scripts(tmp_file)
        self.assertTrue(os._exists(tmp_file))
        os.remove(tmp_file)
        
    
    def tearDown(self):
        pass