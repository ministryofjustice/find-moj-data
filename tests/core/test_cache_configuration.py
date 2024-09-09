from core.helpers import generate_cache_configuration


def test_redis_cache_for_non_local_development(set_redis_cache_env):
    cache = generate_cache_configuration()
    location = cache["default"]["LOCATION"]
    assert len(location) == 3
    assert (
        location[0]
        == "rediss://:testredistoken@master.cp-12345.iwfvzo.euw2.cache.amazonaws.com/0"
    )
    assert cache["default"]["BACKEND"] == "django.core.cache.backends.redis.RedisCache"


def test_memcache_for_local_development(unset_redis_cache_env):
    cache = generate_cache_configuration()
    assert "LOCATION" not in cache["default"]
    assert (
        cache["default"]["BACKEND"] == "django.core.cache.backends.locmem.LocMemCache"
    )
