import redis
import logging
import uuid
from doc_converter.common.util import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT


logger = logging.getLogger(__name__)


class RedisWrapper(object):
    def __init__(self, default_expire_time=300):
        self.r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
        self.default_expire_time = default_expire_time
        try:
            test_key = "doc_converter_connection_test-" + str(uuid.uuid4)
            if not self.r.set(test_key, "test_value", ex=1):
                raise redis.RedisError
            else:
                logger.info("Redis Connected at {0}:{1}".format(REDIS_HOST, REDIS_PORT))
        except Exception as ex:
            logger.exception(ex)
            logger.error("Redis Failed to Connect.  If you intent to run this application without redis, please set the USE_REDIS environment variable to False.")

    def store(self, filepath, blob_name):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = f.read()
        success = self.r.set(blob_name, data, ex=self.default_expire_time)
        if not success:
            logger.error("Unable to store converted file in Redis Db.")
            