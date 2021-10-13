""" Utilities for the doc_converter microservice """
import logging
import sys
import os
import lxml
import lxml.etree
from environs import Env
from logging.config import dictConfig
from wsgi_microservice_middleware import RequestIdFilter, RequestIdJsonLogFormatter

os.environ['LC_ALL'] = 'C.UTF-8'
os.environ['LANG'] = 'C.UTF-8'

env = Env()
env.read_env()

if env.bool("DEBUG", False) or not env.bool('JSON_LOGGER', True):
    log_formatter = 'default'
    log_level = 'DEBUG'
else:
    log_formatter = 'json'
    log_level = 'INFO'

logger_settings = {
    'version': 1,
    'filters': {
        'request_id_filter': {
            '()': RequestIdFilter,
        }
    },
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(request_id)s -  %(message)s',
        },
        'json': {
            "()": RequestIdJsonLogFormatter
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'formatter': log_formatter,
            'filters': ['request_id_filter']
        },
    },
    'root': {
        'level': log_level,
        'handlers': ['wsgi']
    }
}

dictConfig(logger_settings)
logger = logging.getLogger(__name__)
logging.getLogger('multipart.multipart').setLevel(logging.INFO)


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


REDIS_HOST = env.str("REDIS_HOST", "0.0.0.0")

REDIS_PASSWORD = env.str("REDIS_PASSWORD", None)

REDIS_PORT = env.str("REDIS_PORT", "6379")

USE_REDIS = env.bool("USE_REDIS", True)

USE_BLOB = env.bool("USE_BLOB", True)

CACHE_EXPIRY_SECONDS = env.int("CACHE_EXPIRY_SECONDS", 300)

ROOT_PATH = env.str("ROOT_PATH", None)

TEMP_FOLDER = '/tmp/convert'

MAX_JOB_RETRIES = env.int("MAX_JOB_RETRIES", 3)

EVENT_BROKER_URL = env.str("EVENT_BROKER_URL", None)

EVENT_SOURCE = env.str("EVENT_SOURCE", "https://doc-converter.api.presalytics.io")
