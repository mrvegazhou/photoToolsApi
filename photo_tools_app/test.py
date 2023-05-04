# -*- coding: utf-8 -*-
# @DateTime : 2022/8/25 17:38
# @Author   : charlesxie
import threading
import uuid
import weakref

import redis
import time

LOCK_SCRIPT = b"""
if (redis.call('exists', KEYS[1]) == 0) then
    redis.call('hincrby', KEYS[1], ARGV[2], 1);
    redis.call('expire', KEYS[1], ARGV[1]);
    return 1;
end ;
if (redis.call('hexists', KEYS[1], ARGV[2]) == 1) then
    redis.call('hincrby', KEYS[1], ARGV[2], 1);
    redis.call('expire', KEYS[1], ARGV[1]);
    return 1;
end ;
return 0;
"""
UNLOCK_SCRIPT = b"""
if (redis.call('hexists', KEYS[1], ARGV[1]) == 0) then
    return nil;
end ;
local counter = redis.call('hincrby', KEYS[1], ARGV[1], -1);
if (counter > 0) then
    return 0;
else
    redis.call('del', KEYS[1]);
    return 1;
end ;
return nil;
"""
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


class RedisLock:
    """
    redis实现互斥锁，支持重入和续锁
    """

    def __init__(self, conn, lock_name, expire=30, uid=None, is_renew=True):
        self.conn = conn
        self.lock_script = None
        self.unlock_script = None
        self.renew_script = None
        self.register_script()

        self._name = f"lock:{lock_name}"
        self._expire = int(expire)
        self._uid = uid or str(uuid.uuid4())

        self._lock_renew_interval = self._expire * 2 / 3
        self._lock_renew_threading = None

        self.is_renew = is_renew
        self.is_acquired = None
        self.is_released = None

    @property
    def id(self):
        return self._uid

    @property
    def expire(self):
        return self._expire

    def acquire(self):
        result = self.lock_script(keys=(self._name,), args=(self._expire, self._uid))
        if self.is_renew:
            self._start_renew_threading()
        self.is_acquired = True if result else False
        print(f"争抢锁：{self._uid}-{self.is_acquired}\n")
        return self.is_acquired

    def release(self):
        if self.is_renew:
            self._stop_renew_threading()

        result = self.unlock_script(keys=(self._name,), args=(self._uid,))
        self.is_released = True if result else False
        print(f"释放锁{self.is_released}")
        return self.is_released

    def register_script(self):
        self.lock_script = self.conn.register_script(LOCK_SCRIPT)
        self.unlock_script = self.conn.register_script(UNLOCK_SCRIPT)
        self.renew_script = self.conn.register_script(RENEW_SCRIPT)

    def renew(self, renew_expire=30):
        result = self.renew_script(keys=(self._name,), args=(renew_expire,))
        if result == 1:
            raise Exception(f"{self._name} 没有获得锁或锁过期！")
        elif result == 2:
            raise Exception(f"{self._name} 未设置过期时间")
        elif result:
            raise Exception(f"未知错误码: {result}")
        print("续命一波", result)

    @staticmethod
    def _renew_scheduler(weak_self, interval, lock_event):
        print("interval:", interval)
        while not lock_event.wait(timeout=interval):
            lock = weak_self()
            print(lock, "--lock--")
            if lock is None:
                break
            lock.renew(renew_expire=lock.expire)
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
        self.acquire()
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        print("__exit__")
        self.release()


def run_work(my_user_id):
    with RedisLock(redis_client, "test", uid=my_user_id, expire=5) as r:
        if r.is_acquired:
            print(f"just do it,{my_user_id}")
            time.sleep(5)
        else:
            print(f"quit,,,,, {my_user_id}")


if __name__ == '__main__':
    redis_client = redis.Redis(host="localhost", port=6379, db=2)
    a1 = threading.Thread(target=run_work, args=("charles",))
    # a2 = threading.Thread(target=run_work, args=("xie",))

    a1.start()
    # a2.start()

