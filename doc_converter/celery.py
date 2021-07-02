import logging, os
from doc_converter.processmgr.processmgr import ProcessMgr
from doc_converter.processmgr.redis_wrapper import RedisWrapper
from doc_converter import util
from celery import Celery
from celery.signals import setup_logging
from celery.utils.log import get_task_logger


logger = logging.getLogger(__name__)


CELERY_BROKER_URL = 'redis://:{0}@{1}:{2}/0'.format(util.REDIS_PASSWORD, util.REDIS_HOST, util.REDIS_PORT)


celery_app = Celery()
celery_app.conf.broker_url = CELERY_BROKER_URL

@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig
    from doc_converter.util import logger_settings
    dictConfig(logger_settings)


@celery_app.task(autoretry_for=(Exception,))
def convert_task(redis_key):
    try:
        r = RedisWrapper.get_redis()
        pickle_data = r._redis.get(redis_key)
        process_mgr = ProcessMgr.deserailize(pickle_data)
        process_mgr.convert()
    except Exception as ex:
        task_logger = get_task_logger(__name__)
        task_logger.exception(ex)
        raise ex

