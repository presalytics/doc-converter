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
- url: https://api.presalytics.io/doc-converter/
  description: Base server
  variables:
    protocol:
      enum:
      - https
      default: https

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


app.register_blueprint(dc, url_prefix=app.config['APPLICATION_ROOT'])

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
