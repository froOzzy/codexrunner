import sys
import typing

import redis
from django.conf import settings


class RedisPoolLazySingleton:
    _redis_pools: typing.Dict[str, redis.ConnectionPool] = {}

    def __new__(cls, connection_params, as_bytes, logger=None):
        connection_key = (connection_params.get('connection_label', 'default'), as_bytes)
        if connection_key not in RedisPoolLazySingleton._redis_pools:
            if logger:
                logger.info('connect_to_redis')
            db = 0
            if 'test' in sys.argv or 'pytest' in sys.modules:
                db = 3
            RedisPoolLazySingleton._redis_pools[connection_key] = redis.ConnectionPool(
                host=connection_params['host'],
                port=connection_params['port'],
                password=connection_params['password'],
                db=db,
                max_connections=connection_params['max_connections_for_pool'],
                decode_responses=not as_bytes
            )
        return RedisPoolLazySingleton._redis_pools[connection_key]


def redis_connection(connection_params=None, as_bytes=False, logger=None):
    if connection_params is None:
        connection_params = settings.DEFAULT_REDIS
    return redis.Redis(connection_pool=RedisPoolLazySingleton(connection_params, as_bytes, logger))