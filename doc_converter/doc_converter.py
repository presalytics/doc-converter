""" 
RPC API to convert file formats leveraging libreoffice subprocesses 
doc_converter.py contains main application loop and api routing
"""
import os
from flask import Flask, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from common import util # Loads static functions for module and constants
from processmgr import allowed_file
from models import InvalidUsage
logger = util.logger

doc_converter = Flask(__name__)
doc_converter.config.from_pyfile('config.py')

@doc_converter.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    logger.error(error)
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@doc_converter.route("/")
def hello():
    """ test function """
    return "hello world!"

@doc_converter.route('/invalidfile')
def invalid_file():
    """ Exception for invalid file extensions """
    raise InvalidUsage("Invalid file type uploaded", status_code=415)

@doc_converter.route('/badrequest')
def bad_request():
    """ extension for catch all api errors based on client input """
    raise InvalidUsage("Bad request.  Inspect method allow request formats.", status_code=400)

@doc_converter.route('/svgconvert', methods=['GET', 'POST'])
def svgconvert():
    """ Converts the uploaded file to an svg file. """
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('bad_request'))
        file = request.files['file']
        if file.filename == '':
            return redirect(url_for('invalid_file'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(doc_converter.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            

if __name__ == '__main__':
    doc_converter.run()
