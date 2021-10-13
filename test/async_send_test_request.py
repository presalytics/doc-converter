import requests
import uuid
from pathlib import Path


test_file = Path(__file__).parent.joinpath("files").joinpath("Rectangle.pptx")

r = requests.post('http://localhost:8080/convert', files={
    'file': ('Rectangle.pptx', open(test_file, 'rb'), 'application/vnd.openxmlformats-officedocument.presentationml.presentation'),
    'userId': (None, str(uuid.uuid4())),
    'id': (None, str(uuid.uuid4())),
    'convertType': (None, 'svg')
})

print(r.status_code)
