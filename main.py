import uvicorn
from doc_converter.app import app

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080, debug=True, workers=1, log_level='debug')
