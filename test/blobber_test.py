import sys, unittest, os, json
top_level = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, top_level)

import doc_converter.storage.storagewrapper

class BlobberTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_blob_allocation(self):
        blobber = doc_converter.storage.storagewrapper.Blobber()
        blob_name = blobber.allocate_blob()
        ret_dict = {
            'blob_name': blob_name,
            'blob_url': blobber.get_blob_uri(blob_name=blob_name)
        }
        ret_json = json.dumps(ret_dict)
        loaded = json.loads(ret_json)
        self.assertEqual(ret_dict, loaded)

        

    def tearDown(self):
        pass