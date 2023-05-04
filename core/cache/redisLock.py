# -*- coding: utf-8 -*-
import uuid, redis, math, time, weakref, threading


class RedisLock:
    def __init__(self, redis_client=None, lock_key=None, is_renew=True, lock_timeoout=None):
        self.redis_client = redis_client
        self.lock_key = lock_key
        # 是否开启续锁
        self.is_renew = is_renew

        self.lock_timeoout = lock_timeoout

        self._lock_renew_interval = math.ceil(self.lock_timeoout * 2 / 3)
        self._lock_renew_threading = None

        self.is_acquired = None
        self.is_released = None

    def acquire_lock(self, uuid_str=None, lock_timeoout=None):
        """获取锁
            @param lockname:   锁名称
            @param acquire_timeout: 客户端获取锁的超时时间（秒）, 默认3s
            @param lock_timeout: 锁过期时间（秒）, 超过这个时间锁会自动释放, 默认2s
        """
        if not self.lock_key:
            return False
        lockname = self.get_lock_key()
        identifier = uuid_str or str(uuid.uuid4())
        self.identifier = identifier
        lock_timeoout = math.ceil(lock_timeoout) if lock_timeoout else math.ceil(self.lock_timeoout)
        try:
            result = self.redis_client.set(lockname, identifier, nx=True, ex=lock_timeoout) # ex:过期时间（秒）；px:过期时间（毫秒）
            if self.is_renew:
                self._start_renew_threading()
            self.is_acquired = True if result else False
            return self.is_acquired
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
            pass

    def get_release_lua_script(self):
        RELEASE_LUA_SCRIPT = b"""
            if redis.call("get",KEYS[1]) == ARGV[1] then
                return redis.call("del",KEYS[1])
            else
                return 0
            end
        """
        return RELEASE_LUA_SCRIPT

    def get_renew_lua_script(self):
        RENEW_SCRIPT = b"""
            if redis.call("exists", KEYS[1]) == 0 then
                return 1
            elseif redis.call("ttl", KEYS[1]) < 0 then
                return 2
            else
                redis.call("expire", KEYS[1], ARGV[1])
                return 0
            end
        """
        return RENEW_SCRIPT

    def get_lock_key(self):
        return f"lock:{self.lock_key}"

    def release_lock_by_lua(self):
        if self.is_renew:
            self._stop_renew_threading()
        lockname = self.get_lock_key()
        try:
            # 释放锁要验证值
            cmd = self.redis_client.register_script(self.get_release_lua_script())
            res = cmd(keys=(lockname,), args=(self.identifier,))
            self.is_released = True if res else False
            return self.is_released
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
            return None

    def release_lock(self):
        if self.is_renew:
            self._stop_renew_threading()
        with self.redis_client.pipeline() as pipe:
            lockname = self.get_lock_key()
            while True:
                try:
                    pipe.watch(lockname)
                    id = pipe.get(lockname)
                    if id and id == self.identifier:
                        pipe.multi()
                        pipe.delete(lockname)
                        pipe.execute()  # 执行EXEC命令后自动执行UNWATCH （DISCARD同理）
                        return True
                    pipe.unwatch()
                    break
                except redis.WatchError:
                    pass
            return False

    def renew_lock(self, renew_expire):
        lockname = self.get_lock_key()
        cmd = self.redis_client.register_script(self.get_renew_lua_script())
        result = cmd(keys=(lockname,), args=(renew_expire,))
        if result == 1:
            raise Exception(f"{self.lock_key} 没有获得锁或锁过期！")
        elif result == 2:
            raise Exception(f"{self.lock_key} 未设置过期时间")
        elif result:
            raise Exception(f"未知错误码: {result}")
        print("续约。。。")

    @staticmethod
    def _renew_scheduler(weak_self, interval, lock_event):
        while not lock_event.wait(timeout=interval):
            lock = weak_self()
            if lock is None:
                break
            lock.renew_lock(renew_expire=lock.lock_timeoout)
            del lock

    def _start_renew_threading(self):
        self.lock_event = threading.Event()
        self._lock_renew_threading = threading.Thread(target=self._renew_scheduler,
                                                      kwargs={
                                                          "weak_self": weakref.ref(self),
                                                          "interval": self._lock_renew_interval,
                                                          "lock_event": self.lock_event
                                                      })
        self._lock_renew_threading.demon = True
        self._lock_renew_threading.start()

    def _stop_renew_threading(self):
        if self._lock_renew_threading is None or not self._lock_renew_threading.is_alive():
            return
        self.lock_event.set()
        # join 作用是确保thread子线程执行完毕后才能执行下一个线程
        self._lock_renew_threading.join()
        self._lock_renew_threading = None

    def __enter__(self):
        self.acquire_lock()
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        print("__exit__", self.lock_timeoout)
        self.release_lock_by_lua()


if __name__ == "__main__":
    from threading import Thread
    # Redis 存字符串返回的是byte,指定decode_responses=True可以解决
    pool = redis.ConnectionPool(host="127.0.0.1", port=6379, socket_connect_timeout=3, decode_responses=True)
    redis_cli = redis.Redis(connection_pool=pool)

    count = 10
    rl = RedisLock()
    def ticket(i):
        identifier = rl.acquire_lock(redis_cli, 'Ticket')
        print(f"线程{i}--获得了锁")
        time.sleep(1)
        global count
        if count < 1:
            print(f"线程{i}没抢到票, 票已经抢完了")
            return
        count -= 1
        print(f"线程{i}抢到票了, 还剩{count}张票")
        rl.release_lock(redis_cli, 'Resource', identifier)
        print(f"线程{i}--释放了锁")


    for i in range(10):
        t = Thread(target=ticket, args=(i,))
        t.start()