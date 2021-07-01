import unittest, os, shutil, sys, time

top_level = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, top_level)
os.environ['NO_PROXY'] = '127.0.0.1'

import requests

class PngIntegrationTest(unittest.TestCase):

    def test_show_png(self):
        server = 'http://127.0.0.1:8080/doc-converter'
        fpath = os.path.join(os.path.dirname(__file__), 'files', 'Rectangle.pptx')
        png_data = None
        f = {'file': open(fpath, 'rb')}
        png_response = requests.post( server + '/pngconvert', files=f)
        png_data = png_response.json()
        if png_data:
            png_url = png_data["url"]
            png_data = 'temp'
            retries = 0
            while png_data == 'temp':
                png_response = requests.get(png_url)
                if png_response.status_code == 200:
                    png_data = png_response.content
                    fname = 'tmp.png'
                    try:
                        os.remove(fname)
                    except Exception:
                        pass
                    with open(fname, 'wb+') as f:
                        f.write(png_data)
                elif retries > 10:
                    raise Exception('This png does not exist')
                elif png_response.status_code == 202:
                    time.sleep(2)
                    retries += 1
                else:
                    raise Exception('This png does not exist')
                


        

        