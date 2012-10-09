flask-cache-debugpanel
======================

antoher shameless ripoff of a django plugin.
see https://github.com/jbalogh/django-debug-cache-panel

do soemthing like

cache = Cache()

def init_wrapper():
    wrapper = CacheWrapper(cache.cache)
    cache.cache = wrapper

    cache_debug_panel.wrapper = wrapper

