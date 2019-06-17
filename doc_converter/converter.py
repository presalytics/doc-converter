"""
RPC API to convert file formats leveraging libreoffice subprocesses
doc_converter.py contains main application loop and api routing
"""
import os, sys, traceback, json, uuid, time, yaml
from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin
from apispec.utils import validate_spec
from flask import Flask, request, jsonify, redirect, url_for, send_file, Blueprint
from werkzeug.utils import secure_filename
from common import util# Loads static functions for module, constansts and an environment variables, should be 1st import
from models.invalid_usage import InvalidUsage
from processmgr.convert_types import ConvertTypes
from processmgr.processmgr import ProcessMgr
from storage.storagewrapper import Blobber
import spooler 
from common import cleaner # cron job for temp file cleanup

logger = util.logger

app = Flask(__name__)
app.config.from_pyfile('config.py')

blobber = Blobber()

dc = Blueprint(app.config['APPLICATION_ROOT'], __name__)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """ Handles invalid_usage errors """
    logger.error(error)
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@dc.route("/")
def hello():
    """ 
    test function to  indicate api is communications
    
    Returns: "Hello
    ---
    get:
        description: Test function to get return inforation
        summary: Says Hello
        operationId: SayHello
        responses:
            200:
                description: OK
                content:
                    application/json:
                        schema:
                            title: Hello
                            type: string

    """
    return "hello world!"

@dc.route('/invalidfile')
def invalid_file():
    """ Exception for invalid file extensions """
    raise InvalidUsage("Invalid file type uploaded", status_code=415)

@dc.route('/badrequest')
def bad_request():
    """ extension for catch all api errors based on client input """
    raise InvalidUsage("Bad request.  Inspect method allow request formats.", status_code=400)

@dc.route('/servererror')
def server_error():
    """ Exception catch all for client errors based on server problems """
    raise InvalidUsage("Internal server error.  Please review debug logs", status_code=502)

@dc.route('/timeout')
def timeout_error():
    """ Exception to catch designed-in timeout errors (large-files, etc.) """
    raise InvalidUsage("Timeout Error.  Please retry and/or break up file size.")

@dc.route('/svgconvert', methods=['POST'])
def svgconvert():
    """ 
    Converts the uploaded file to an svg file. 
    ---
    post:
        summary: converts pptx file to svg image
        operationId: ConvertToSvg
        requestBody:
            description: Filepath to pptx file
            required: True
            content:
                multipart/form-data:
                    schema:
                        title: File to Convert
                        type: object
                        properties:
                            file:
                                type: string
                                format: binary

        responses:
            200:
                description: Url of svg file
                content:
                    application/json:
                        schema:
                            type: string
                            title: File Url
                            description: url of converted file
            400:
                description: Bad Request.
            415:
                description: Invalid file type
            

    """
    try: 
        if request.method == 'POST':
            if 'file' not in request.files:
                logger.debug("Malformed request: file not included in post data")
                return redirect(url_for('bad_request'))
            file = request.files['file']
            if file.filename == '':
                return redirect(url_for('invalid_file'))
            if file and ProcessMgr.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                blob_name = blobber.allocate_blob()
                temp_filename = blob_name + "." + ProcessMgr.get_file_extension(filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
                try:
                    os.remove(filepath)
                except:
                    pass
                file.save(filepath)
                try:
                    convert_obj = ProcessMgr(
                        in_filepath=filepath,
                        convert_type=ConvertTypes.SVG,
                        out_dir=app.config['DOWNLOAD_FOLDER'],
                        blob_name=blob_name
                    )
                    convert_obj.spool()
                    return blobber.get_blob_uri(blob_name=blob_name)
                except IOError as err:
                    logger.exception(err)
                    return redirect(url_for('server_error'))

        elif request.method == 'GET':
            logger.debug("Unallowed Method")
            return redirect(url_for('bad_request'))
    except Exception as err:
        logger.exception(err)
        return redirect(url_for('bad_request'))


        return send_file()
    else:
        return redirect(url_for('bad_request'))


OPENAPI_BASE = """
openapi: 3.0
info:
  description: This api converts file formats of OpenXml and OpenOffice documents formats to vector files (e.g., svg)
  title: Doc Converter
  version: 0.1.0
  contact:
    name: Presalytics.io
    url: http://presalytics.io
    email: kevin@presalytics.io
  license:
    name: AGPL

servers:
- url: http://api.presalytics.io/doc-converter
  description: Base server
  variables:
    protocol:
      enum:
      - http
      default: http

"""

settings = yaml.safe_load(OPENAPI_BASE)
# retrieve  title, version, and openapi version
title = settings["info"].pop("title")
spec_version = settings["info"].pop("version")
openapi_version = settings.pop("openapi")

spec = APISpec(
    title="Doc Converter",
    version="0.1",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin()],
    **settings
)


app.register_blueprint(dc)

with app.test_request_context():
    spec.path(view=svgconvert)
    spec.path(view=hello)

validate_spec(spec)

open_api_file = "/srv/doc_converter/doc_converter/docs/openapi.json"


with open(open_api_file, "w") as apifile:
    json.dump(spec.to_dict(), apifile, indent=4)

@app.route("/doc-converter/docs/openapi.json")
def openapi_json():
    return send_file(open_api_file)


if __name__ == '__main__':
    app.run()
