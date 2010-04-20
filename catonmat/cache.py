#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.config            import config

import memcache

# ----------------------------------------------------------------------------

mc = memcache.Client(['127.0.0.1:11211'])


def cache(key, duration=0):
    def _cache(function):
        def __cache(*args, **kw):
            if not config.use_cache:
                return function(*args, **kw)

            value = cache_get(key)
            if value is not None:
                return value

            value = function(*args, **kw)
            cache_set(key, value, duration)
            return value
        return __cache
    return _cache


def cache_get(key):
    return mc.get(str(key))


def cache_set(key, value, duration=0):
    mc.set(str(key), value, duration)


def cache_del(key):
    mc.delete(str(key))


class MemcachedNone(object):
    pass

def from_cache_or_compute(computef, key, duration, *args, **kw):
    if not config.use_cache:
        return computef(*args, **kw)

    cached_data = cache_get(key)
    if isinstance(cached_data, MemcachedNone):
        return None
    if cached_data is not None:
        return cached_data
    
    # if data is not cached, compute, cache and return it
    cached_data = computef(*args, **kw)
    if cached_data is None:
        cache_set(key, MemcachedNone(), duration)
    else:
        cache_set(key, cached_data, duration)
    return cached_data

