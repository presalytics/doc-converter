from doc_converter.storage.base import FileStorageBase
from doc_converter.storage.redis_wrapper import RedisWrapper


class CacheStore(FileStorageBase):
    def __init__(self, *args, **kwargs) -> None:
        super(CacheStore, self).__init__(*args)

    def allocate_key(self):
        r = RedisWrapper.get_redis()
        r._redis.set(self.key, b'\x00')

    def get_file(self):
        r = RedisWrapper.get_redis()
        r._redis.get(self.key)

    def put_file(self, filepath: str) -> None:
        r = RedisWrapper.get_redis()
        r.store(filepath, self.key)

    def clean(self) -> None:
        r = RedisWrapper.get_redis()
        r._redis.delete(self.key)
