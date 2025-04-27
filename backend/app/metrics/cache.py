# backend/app/metrics/cache.py
import time, functools
def ttl_cache(seconds=30):
    def wrapper(fn):
        store = {}
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            t, val = store.get("x", (0, None))
            if time.time() - t > seconds:
                val = fn(*args, **kwargs)
                store["x"] = (time.time(), val)
            return val
        return inner
    return wrapper
