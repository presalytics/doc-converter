import logging
import os
from celery import Celery
from celery.app import autoretry
from celery.signals import setup_logging
from doc_converter.spooler.uno_controller import UnoConverter
from doc_converter.common.util import (
    REDIS_HOST, 
    REDIS_PASSWORD, 
    REDIS_PORT,
)
from doc_converter.config import UPLOAD_FOLDER, DOWNLOAD_FOLDER
from unotools.errors import ConnectionError



logger = logging.getLogger(__name__)

CELERY_BROKER_URL = 'redis://:{0}@{1}:{2}/0'.format(REDIS_PASSWORD, REDIS_HOST, REDIS_PORT)


celery_app = Celery()
celery_app.conf.broker_url = CELERY_BROKER_URL

@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig
    from doc_converter.common.util import logger_settings
    dictConfig(logger_settings)

@celery_app.task(autoretry_for=(ConnectionError,))
def png_task(redis_key, file_extension, convert_type):
    from doc_converter.processmgr.processmgr import ProcessMgr
    from doc_converter.storage.redis_wrapper import RedisWrapper
    try:
        logger.debug("Png spooler request received")
        temp_filename = redis_key + "." + file_extension
        filepath = os.path.join(UPLOAD_FOLDER, temp_filename)
        r = RedisWrapper.get_redis()
        try:
            os.remove(filepath)
        except Exception:
            pass
        with open(filepath, 'wb+') as f:
            f.write(r._redis.get(redis_key + '-file'))
        converter = UnoConverter(input_dir=UPLOAD_FOLDER, output_dir=DOWNLOAD_FOLDER)
    
        fpath = converter.convert(filepath, convert_type)
        r.store(fpath, redis_key)
        os.remove(filepath)
        logger.debug("Png spooler request completed")
    except Exception as ex:
        logger.exception(ex)

@celery_app.task
def svg_task(**kwargs):
    logger.info('Task "svg_task" reserved for future use.')

