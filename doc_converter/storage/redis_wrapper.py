import redis
import logging
import json
import presalytics
import datetime
import typing
from doc_converter.common.util import CACHE_EXPIRY_SECONDS, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT


logger = logging.getLogger(__name__)


redis_connection_pool = redis.BlockingConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    health_check_interval=30,
    timeout=10
)


class RedisWrapper(object):
    USE_REDIS = True

    def __init__(self, test_connection=False, *args, **kwargs):
        self._redis = self.make_client()

        if test_connection:
            self.test_connection()

    def make_client(self):
        return redis.StrictRedis(connection_pool=redis_connection_pool)

    def get(self, key):
        queried = False
        attempts = 0
        data = None
        while not queried and attempts < 10:
            try:
                data = self._redis.get(key)
                queried = True
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
                self._redis.connection_pool.disconnect()
                self._redis = self.make_client()
                attempts += 1
        if data:
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                pass
        return data

    def put(self, key, data, expire_seconds: int = CACHE_EXPIRY_SECONDS):
        # allow parent class to handle serialization erros
        # throws `TypeError`
        data = json.dumps(data, cls=presalytics.story.outline.OutlineEncoder)
        queried = False
        attempts = 0
        while not queried and attempts < 10:
            try:
                self._redis.set(key, data)
                queried = True
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
                self._redis.connection_pool.disconnect()
                self._redis = self.make_client()
                attempts += 1
        if expire_seconds:
            if isinstance(expire_seconds, int) or isinstance(expire_seconds, datetime.timedelta):
                self._redis.expire(key, expire_seconds)
            else:
                logger.error("Cache expiry for key {0} could not be set.  expire_seconds must be integer or timedelta.".format(key))

    def store(self, filepath, key):
        with open(filepath, 'rb') as f:
            data = f.read()
        success = self._redis.set(key, data)
        if success:
            self._redis.expire(key, CACHE_EXPIRY_SECONDS)
        else:
            logger.error("Unable to store converted file in Redis Db.")
        
            
    def test_connection(self):
        try:
            self._redis.set('connection_test', 1234)
            logger.info("Connected to redis database at {0}:{1}".format(REDIS_HOST, REDIS_PASSWORD))
            return True
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
            return False

    @classmethod
    def get_redis(cls, test_connection=False) -> typing.Optional['RedisWrapper']:
        if not cls.USE_REDIS:
            return None
        try:
            redis_client = cls(test_connection=test_connection)
        except redis.exceptions.ConnectionError:
            logger.warning("UNABLE TO CONNECT to its REDIS database.  Caching is unavailable.")
            cls.USE_REDIS = False
            return None
        return redis_client