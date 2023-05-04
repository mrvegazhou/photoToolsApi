# -*- coding: utf-8 -*-
import pickle
import redis
from .base import BaseCache


class RedisCache(BaseCache):
    """Uses the Redis key-value store as a cache backend.
    The first argument can be either a string denoting address of the Redis
    server or an object resembling an instance of a redis.Redis class.
    Note: Python Redis API already takes care of encoding unicode strings on
    the fly.
    :param host: address of the Redis server or an object which API is
                 compatible with the official Python Redis client (redis-py).
    :param port: port number on which Redis server listens for connections.
    :param password: password authentication for the Redis server.
    :param db: db (zero-based numeric index) on Redis Server to connect.
    :param default_timeout: the default timeout that is used if no timeout is
                            specified on :meth:`~BaseCache.set`. A timeout of
                            0 indicates that the cache never expires.
    :param key_prefix: A prefix that should be added to all keys.
    Any additional keyword arguments will be passed to ``redis.Redis``.
    """

    def __init__(
        self,
        app = None,
        host = None,
        port = None,
        password = None,
        db = None,
        default_timeout = None,
        key_prefix = None,
        cfg = None,
        **kwargs
    ):
        BaseCache.__init__(self, 300)
        self.host = "localhost"
        self._client = None
        self.port = 6379
        self.password = None
        self.db = 0
        self.default_timeout = 300
        self.key_prefix = ''
        self.app = app
        if app is not None:
            self.init_app(app, host, port, password, db, default_timeout, key_prefix, **kwargs)

    def init_app(self,
                 app,
                 host = "",
                 port = 6379,
                 password = None,   #user+'@'+pwd
                 db = 0,
                 default_timeout = 300,
                 key_prefix = None,
                 ** kwargs
    ):
        self.host = host if host else app.config.get("REDIS_HOST", self.host)
        self.port = port if port else app.config.get("REDIS_PORT", self.port)
        self.password = password if password else app.config.get("REDIS_PASSWORD", self.password)
        self.db = db if db else app.config.get("REDIS_DB", self.db)
        self.default_timeout = default_timeout if default_timeout else app.config.get("REDIS_DEFAULT_TIMEOUT", self.default_timeout)
        self.key_prefix = key_prefix if key_prefix else app.config.get("REDIS_KEY_PREFIX", self.key_prefix)
        if 'pool' in kwargs and kwargs['pool']==False:
            self._client = redis.StrictRedis(host=self.host, port=self.port,
                                             password=self.password, db=self.db, **kwargs)
        else:
            pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db)
            self._client = redis.StrictRedis(host=self.host, port=self.port, connection_pool=pool,
                                             password=self.password, db=self.db, **kwargs)


    def _normalize_timeout(self, timeout):
        timeout = BaseCache._normalize_timeout(self, timeout)
        if timeout == 0:
            timeout = -1
        return timeout

    def dump_object(self, value):
        """Dumps an object into a string for redis.  By default it serializes
        integers as regular string and pickle dumps everything else.
        """
        t = type(value)
        if isinstance(t, int):
            return str(value).encode("ascii")
        return b"!" + pickle.dumps(value)

    def load_object(self, value):
        """The reversal of :meth:`dump_object`.  This might be called with
        None.
        """
        if value is None:
            return None
        if value.startswith(b"!"):
            try:
                return pickle.loads(value[1:])
            except pickle.PickleError:
                return None
        try:
            return int(value)
        except ValueError:
            # before 0.8 we did not have serialization.  Still support that.
            return value

    def get(self, key):
        return self.load_object(self._client.get(self._key(key)))

    def get_many(self, *keys):
        if self.key_prefix:
            keys = [self._key(key) for key in keys]
        return [self.load_object(x) for x in self._client.mget(keys)]

    def set(self, key, value, timeout=None):
        timeout = self._normalize_timeout(timeout)
        dump = self.dump_object(value)
        if timeout == -1:
            result = self._client.set(name=self._key(key), value=dump)
        else:
            result = self._client.setex(
                name=self._key(key), value=dump, time=timeout
            )
        return result

    def add(self, key, value, timeout=None):
        timeout = self._normalize_timeout(timeout)
        dump = self.dump_object(value)
        return self._client.setnx(
            name=self.key_prefix + key, value=dump
        ) and self._client.expire(name=self._key(key), time=timeout)

    def set_many(self, mapping, timeout=None):
        timeout = self._normalize_timeout(timeout)
        # Use transaction=False to batch without calling redis MULTI
        # which is not supported by twemproxy
        pipe = self._client.pipeline(transaction=False)

        for key, value in mapping.items():
            dump = self.dump_object(value)
            if timeout == -1:
                pipe.set(name=self._key(key), value=dump)
            else:
                pipe.setex(name=self._key(key), value=dump, time=timeout)
        return pipe.execute()

    def delete(self, key):
        return self._client.delete(self._key(key))

    def delete_many(self, *keys):
        if not keys:
            return
        if self.key_prefix:
            keys = [self.key_prefix + key for key in keys]
        return self._client.delete(*keys)

    def has(self, key):
        return self._client.exists(self._key(key))

    def clear(self):
        status = False
        if self.key_prefix:
            keys = self._client.keys(self.key_prefix + "*")
            if keys:
                status = self._client.delete(*keys)
        else:
            status = self._client.flushdb()
        return status

    def inc(self, key, delta=1):
        return self._client.incr(name=self._key(key), amount=delta)

    def dec(self, key, delta=1):
        return self._client.decr(name=self._key(key), amount=delta)

    def zcard(self, key):
        return self._client.zcard(self._key(key))

    def zadd(self, key, **kwargs):
        return self._client.zadd(self._key(key), **kwargs)

    def zrem(self, key, *name):
        return self._client.zrem(self._key(key), *name)

    def zincrby(self, key, name, amount=1):
        return self._client.zincrby(self._key(key), name, amount)

    def zrank(self, key, name, desc=False):
        key = self._key(key)
        if desc:
            return self._client.zrevrank(key, name)
        return self._client.zrank(key, name)

    def zscore(self, key, name):
        return self._client.zscore(self._key(key), name)

    def zrange(self, key, start, end, desc=False, withscores=False, score_cast_func=float):
        return self._client.zrange(self._key(key), start, end, desc, withscores, score_cast_func)

    def zrangebyscore(self, key, min_score, max_score, start=None, num=None, withscores=False,
                      score_cast_func=float):
        return self._client.zrangebyscore(self._key(key), min_score, max_score, start, num, withscores,
                                          score_cast_func)

    def lpush(self, key, l):
        return self._client.lpush(self._key(key), *l)

    def rpop(self, key):
        return self._client.lpush(self._key(key))

    def lrange(self, key, start, num):
        return self._client.lrange(self._key(key), start, num)

    def llen(self, key):
        return self._client.llen(self._key(key))

    def lock(self, key, blocking_timeout=None):
        return self._client.lock(self._key(key)) if not blocking_timeout else self._client.lock(self._key(key), blocking_timeout=blocking_timeout)

    def _key(self, key):
        return "{}{}".format(self.key_prefix, key)

    def get_client(self):
        return self._client