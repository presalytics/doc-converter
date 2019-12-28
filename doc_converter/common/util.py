""" Utilities for the doc_converter microservice """
import logging
import sys
import os
import lxml
import lxml.etree
import io
from environs import Env
from logging.config import dictConfig

env = Env()
env.read_env()

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s',
    }},
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

logger = logging.getLogger('doc_converter.util')
logger.info("Web App Logger Initialized")


def handle_exception(exc_type, exc_value, exc_traceback):
    """ Catches unhandled exceiptions for logger """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

def strip_scripts(filename):
    """ function to strip javascript out of svg file to reduce filesize.
        NOTE:  Not implemented.  function works, just need to figure
        out how to load js library front end.

        TODO: add libreoffice scripts to javascript library so svg
            files can be displayed without embedded js.
    """
    svg = lxml.etree.parse(filename)
    root = svg.getroot()
    script_elements = root.findall('.//{*}script')
    for ele in script_elements:
        ele.getparent().remove(ele)
    new_str = lxml.etree.tostring(svg).decode('utf-8')
    new_filename = os.path.join(os.path.dirname(filename), "stripped-" + os.path.basename(filename))
    with open(new_filename, 'w') as outfile:
        outfile.write(new_str)
    return new_filename
