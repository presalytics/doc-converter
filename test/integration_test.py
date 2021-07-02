import unittest, os, sys, time, requests, shutil

top_level = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, top_level)
os.environ['NO_PROXY'] = '127.0.0.1'

class IntegrationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = os.environ.get("TEST_SERVER", 'http://127.0.0.1:8080')
        cls.delete_output = os.getenv("DELETE_TEST_OUTPUT", 'False').lower() in ('true', '1', 't')
        cls.test_filepath = os.path.join(os.path.dirname(__file__), 'files', 'Rectangle.pptx')
        cls.out_dir = os.path.join(os.getcwd(), 'out')
        if os.path.isdir(cls.out_dir):
            cls._clean_out_dir()
        else:
            os.mkdir(cls.out_dir)
        return super(IntegrationTests, cls).setUpClass()

    def test_convert_png(self):
        convert_type = "png"
        file_url = self._convert(convert_type)
        out_file = self._poll_for_file(file_url, convert_type)
        self.assertEqual(os.path.exists(out_file), True)
    
    def test_convert_svg(self):
        convert_type = "svg"
        file_url = self._convert(convert_type)
        out_file = self._poll_for_file(file_url, convert_type)
        self.assertEqual(os.path.exists(out_file), True)

    def _convert(self, convert_type) -> str:
        f = {'file': open(self.test_filepath, 'rb')}
        resp = requests.post( self.server + '/convert/{0}'.format(convert_type), files=f)
        data = resp.json()
        return data["url"]
    
    def _poll_for_file(self, file_url, convert_type) -> str:
        file_bytes = None
        retries = 0
        while not file_bytes:
            resp = requests.get(file_url)
            if resp.status_code == 200:
                file_bytes = resp.content
                fname = os.path.join(self.out_dir, 'Rectangle.' + convert_type)
                with open(fname, 'wb+') as f:
                    f.write(file_bytes)
                return fname
            elif resp.status_code == 202:
                time.sleep(2)
            else:
                raise Exception('Received and unexpected response from the test server')
            retries += 1
            if retries > 10:
                raise Exception('This file does not exist')

    @classmethod
    def _clean_out_dir(self):
        for file_obj in os.listdir(self.out_dir):
            path = os.path.join(self.out_dir, file_obj)
            try:
                shutil.rmtree(path)
            except OSError:
                os.remove(path)
    
    @classmethod
    def tearDownClass(cls):
        if cls.delete_output:
            try:
                shutil.rmtree(cls.out_dir)
            except Exception:
                pass
        return super(IntegrationTests, cls).tearDownClass()



        

        