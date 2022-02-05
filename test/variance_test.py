import requests
import uuid
from pathlib import Path


for i in range(1, 7):
    fname = "{0}.pptx".format(i)
    test_file = Path(__file__).parent.joinpath("files").joinpath(fname)
    r = requests.post('http://localhost:8080/convert', files={
        'file': (fname, open(test_file, 'rb'), 'application/vnd.openxmlformats-officedocument.presentationml.presentation'),
        'userId': (None, str(uuid.uuid4())),
        'id': (None, str(uuid.uuid4())),
        'convertType': (None, 'svg'),
        'storyId': (None, str(uuid.uuid4())),
    })

    print(r.status_code)
