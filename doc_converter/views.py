import sys, os, logging
import connexion
from flask import Flask, request, jsonify, redirect, url_for, send_file, Blueprint
from werkzeug.utils import secure_filename
from doc_converter import config
from doc_converter.common import util# Loads static functions for module, constansts and an environment variables, should be 1st import
from doc_converter.models.invalid_usage import InvalidUsage
from doc_converter.processmgr.convert_types import ConvertTypes
from doc_converter.processmgr.processmgr import ProcessMgr
from doc_converter.storage.storagewrapper import Blobber
from doc_converter.common import cleaner # cron job for temp file cleanup




logger = logging.getLogger('doc_converter.views')

def view_resolver(operation_id):
    """ returns a view function in this module as function of operation id 
        all operation ids should adhere to convention: 'path_subpath_method'
    
    """
    try:
        name = operation_id.rsplit('.', 1)[1]
    except:
        name = operation_id
    function = globals()[operation_id]
    return function

def hello():
    """ 
    test function to  indicate api is communications
    
    Returns: "hello world!"
  
    """
    return "hello world!"


def invalid_file():
    """ Exception for invalid file extensions """
    raise InvalidUsage("Invalid file type uploaded", status_code=415)


def bad_request():
    """ extension for catch all api errors based on client input """
    raise InvalidUsage("Bad request.  Inspect method allow request formats.", status_code=400)


def server_error():
    """ Exception catch all for client errors based on server problems """
    raise InvalidUsage("Internal server error.  Please review debug logs", status_code=502)


def timeout_error():
    """ Exception to catch designed-in timeout errors (large-files, etc.) """
    raise InvalidUsage("Timeout Error.  Please retry and/or break up file size.")


def svgconvert():
    """ 
    Converts the uploaded file to an svg file. 
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
                blobber = Blobber()
                blob_name = blobber.allocate_blob()
                temp_filename = blob_name + "." + ProcessMgr.get_file_extension(filename)
                filepath = os.path.join(config.UPLOAD_FOLDER, temp_filename)
                try:
                    os.remove(filepath)
                except:
                    pass
                file.save(filepath)
                try:
                    convert_obj = ProcessMgr(
                        in_filepath=filepath,
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
    else:
        return redirect(url_for('bad_request'))


