# coding:utf8
import requests

MAX_CONNECTIONS = 50


class CustomedSession(requests.Session):
    def request(self, *args, **kwargs):
        kwargs.setdefault('timeout', 180) # 3min
        return super(CustomedSession, self).request(*args, **kwargs)


session = CustomedSession()
adapter = requests.adapters.HTTPAdapter(pool_connections = MAX_CONNECTIONS,
                                        pool_maxsize = MAX_CONNECTIONS,
                                        max_retries = 5)
session.mount('http://', adapter)
session.mount('https://', adapter)