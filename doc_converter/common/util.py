""" Utilities for the doc_converter microservice """
import logging
import sys
import os
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
