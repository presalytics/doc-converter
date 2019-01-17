""" Utilities for the doc_converter microservice """
import logging
import sys
import os
from environs import Env
import ptvsd

env = Env()
env.read_env()

file_path = os.path.join(os.path.dirname(__file__), '../log/doc_converter.log')
logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


file_handler = logging.FileHandler(file_path)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

log_level = logging.getLevelName(os.environ.get('DocConverterLogLevel'))
logger.setLevel(log_level)

logger.info("Logger Initialized")


def handle_exception(exc_type, exc_value, exc_traceback):
    """ Catches unhandled exceiptions for logger """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

if os.environ.get('DocConverterRemoteDebug') == "True":
    logger.info("Waiting for debugger attach...")
    logger.info(os.environ.get('DocConverterServer'))
    logger.info(os.environ.get('DocConverterRemoteDebugPort'))
    ptvsd.enable_attach(address=(os.environ.get('DocConverterServer'), os.environ.get('DocConverterRemoteDebugPort')), redirect_output=True )
    ptvsd.wait_for_attach()
    ptvsd.break_into_debugger()
    logger.info('Debugger attached.  Proceeding startup.')
    breakpoint()
    