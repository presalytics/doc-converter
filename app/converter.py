"""
RPC API to convert file formats leveraging libreoffice subprocesses
doc_converter.py contains main application loop and api routing
"""
import os, sys, traceback, json, uuid, time
from flask import Flask, request, jsonify, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from app.common import util# Loads static functions for module, constansts and an environment variables, should be 1st import
from app.models.invalid_usage import invalid_usage
from app.processmgr.convert_types import convert_types
from app.processmgr.processmgr import processmgr
from app.storage.storagewrapper import Blobber
import app.spooler 

logger = util.logger

app = Flask(__name__)
app.config.from_pyfile('config.py')


blobber = Blobber()

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

@app.route('/timeout')
def timeout_error():
    """ Exception to catch designed-in timeout errors (large-files, etc.) """
    raise invalid_usage("Timeout Error.  Please retry and/or break up file size.")

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
                blob_name = blobber.allocate_blob()
                temp_filename = blob_name + "." + processmgr.get_file_extension(filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
                try:
                    os.remove(filepath)
                except:
                    pass
                file.save(filepath)
                try:
                    convert_obj = processmgr(
                        in_filepath=filepath,
                        convert_type=convert_types.SVG,
                        out_dir=app.config['DOWNLOAD_FOLDER'],
                        blob_name=blob_name
                    )
                    convert_obj.spool()
                    return blobber.get_blob_uri(blob_name=blob_name)
                except IOError as err:
                    logger.exception(err)
                    return redirect(url_for('server_error'))

        elif request.method == 'GET':
            return redirect(url_for('bad_request'))
    except Exception as err:
        logger.exception(err)
        return redirect(url_for('bad_request'))


        return send_file()
    else:
        return redirect(url_for('bad_request'))


if __name__ == '__main__':
    app.run()
