# backend/app/metrics/cache.py - FIXED VERSION
import time
import functools
import hashlib

def ttl_cache(seconds=30):
    def wrapper(fn):
        # Each function gets its own cache store
        cache_store = {}
        
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            # Create unique cache key based on function name and arguments
            key_data = f"{fn.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            timestamp, cached_value = cache_store.get(cache_key, (0, None))
            
            # Check if cache has expired
            if time.time() - timestamp > seconds:
                # Cache miss or expired - call the actual function
                cached_value = fn(*args, **kwargs)
                cache_store[cache_key] = (time.time(), cached_value)
                print(f"Cache MISS for {fn.__name__} - fetched fresh data")
            else:
                print(f"Cache HIT for {fn.__name__} - using cached data (age: {int(time.time() - timestamp)}s)")
                
            return cached_value
            
        # Add method to clear cache for debugging
        def clear_cache():
            cache_store.clear()
            print(f"Cache cleared for {fn.__name__}")
            
        inner.clear_cache = clear_cache
        return inner
    return wrapper
