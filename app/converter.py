"""
RPC API to convert file formats leveraging libreoffice subprocesses
doc_converter.py contains main application loop and api routing
"""
import os, sys, traceback
from flask import Flask, request, jsonify, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from app.common import util# Loads static functions for module, constansts and an environment variables, should be 1st import
from app.models.invalid_usage import invalid_usage
from app.processmgr.convert_types import convert_types
from app.processmgr.processmgr import processmgr

logger = util.logger

app = Flask(__name__)
app.config.from_pyfile('config.py')

@app.errorhandler(invalid_usage)
def handle_invalid_usage(error):
    """ Handles invalid_usage errors """
    logger.error(error)
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route("/")
def hello():
    """ test function """
    return "hello world!"

@app.route('/invalidfile')
def invalid_file():
    """ Exception for invalid file extensions """
    raise invalid_usage("Invalid file type uploaded", status_code=415)

@app.route('/badrequest')
def bad_request():
    """ extension for catch all api errors based on client input """
    raise invalid_usage("Bad request.  Inspect method allow request formats.", status_code=400)

@app.route('/servererror')
def server_error():
    """ Exception catch all for client errors based on server problems """
    raise invalid_usage("Internal server error.  Please review debug logs", status_code=502)

@app.route('/svgconvert', methods=['GET', 'POST'])
def svgconvert():
    """ Converts the uploaded file to an svg file. """
    try: 
        if request.method == 'POST':
            if 'file' not in request.files:
                return redirect(url_for('bad_request'))
            file = request.files['file']
            if file.filename == '':
                return redirect(url_for('invalid_file'))
            if file and processmgr.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    os.remove(filepath)
                except:
                    pass
                file.save(filepath)
                try:
                    convert_obj = processmgr(filepath, convert_types.SVG, app.config['DOWNLOAD_FOLDER']) # 
                    outpath = convert_obj.convert()
                    return send_file(outpath, mimetype="image/svg+xml")
                except IOError as err:
                    logger.exception(err)
                    return redirect(url_for('server_error'))

        elif request.method == 'GET':
            return redirect(url_for('bad_request'))
    except Exception as err:
        logger.exception(err)
        return redirect(url_for('bad_request'))




if __name__ == '__main__':
    app.run()
