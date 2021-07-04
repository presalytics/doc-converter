import unittest
import os
import sys
import shutil

top_level = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, top_level)
os.environ['NO_PROXY'] = '127.0.0.1'


from doc_converter.app_wrapper import DocConverter


class IntegrationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.delete_output = os.getenv("DELETE_TEST_OUTPUT", 'False').lower() in ('true', '1', 't')
        cls.test_filepath = os.path.join(os.path.dirname(__file__), 'files', 'Rectangle.pptx')
        cls.doc_converter = DocConverter(clean_dirs=False, filepath=cls.test_filepath)
        return super(IntegrationTests, cls).setUpClass()

    def test_convert_png(self):
        self.doc_converter.run("png")
        out_file = os.path.join(self.doc_converter.out_dir, "Rectangle.png")
        self.assertEqual(os.path.exists(out_file), True)

    def test_convert_svg(self):
        self.doc_converter.run("svg")
        out_file = os.path.join(self.doc_converter.out_dir, "Rectangle.svg")
        self.assertEqual(os.path.exists(out_file), True)

    @classmethod
    def tearDownClass(cls):
        del cls.doc_converter
        if cls.delete_output:
            try:
                shutil.rmtree(cls.out_dir)
            except Exception:
                pass
        return super(IntegrationTests, cls).tearDownClass()
