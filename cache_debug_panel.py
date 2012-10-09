"""shameless copy of the django cache debug panel"""
import time

from flask import render_template

from flask_debugtoolbar.panels import DebugPanel

def _(key):
    return key

wrapper = None

class CachePanel(DebugPanel):

    name = 'Cache'
    has_content = True

    def nav_title(self):
        return _('Cache')

    def title(self):
        return _('Cache Queries')

    def nav_subtitle(self):
        # Aggregate stats.
        stats = {'hit': 0, 'miss': 0, 'time': 0}
        for log in wrapper.log:
            if hasattr(log, 'hit'):
                stats[log.hit and 'hit' or 'miss'] += 1
            stats['time'] += log.time

        # No ngettext, too many combos!
        stats['time'] = round(stats['time'], 2)
        return _('%(hit)s hits, %(miss)s misses in %(time)sms') % stats

    def content(self):
        context = {'logs': wrapper.log}
        return render_template('debug/cachepanel.jinja.html', **context)

    def url(self):
        return ''

    def process_request(self, request):
        wrapper.reset()


class CacheLog(object):

    def __init__(self, name, key):
        self.name = name
        self.key = key


def logged(f):
    name = f.__name__
    def wrapper(self, key, *args, **kwargs):
        # Store the log here so the wrapper functions can update it.
        self.log.append(CacheLog(name, key))
        t = time.time()

        val = f(self, key, *args, **kwargs)

        self.log[-1].time = 1000 * (time.time() - t)
        return val

    return wrapper


class CacheWrapper(object):
    """Subclass of the current cache backend."""

    def __init__(self, cache):
        # These are the methods we're going to replace.
        methods = 'add get set delete get_many delete_many'.split()

        # Store copies of the true methods.
        self.real_methods = dict((m, getattr(cache, m)) for m in methods)

        # Hijack the cache object.
        for method in methods:
            setattr(cache, method, getattr(self, method))

        self.cache = cache
        self.reset()

    def reset(self):
        self.log = []

    @logged
    def add(self, key, value, timeout=None):
        return self.real_methods['add'](key, value, timeout)

    @logged
    def get(self, *args, **kwargs):
        val = self.real_methods['get'](*args, **kwargs)
        self.log[-1].hit = val is not None
        return val

    @logged
    def set(self, key, value, timeout=None):
        return self.real_methods['set'](key, value, timeout)

    @logged
    def delete(self, key):
        return self.real_methods['delete'](key)

    @logged
    def get_many(self, *keys):
        val = self.real_methods['get_many'](*keys)
        self.log[-1].hit = bool(val)
        return val

    @logged
    def delete_many(self, keys):
        val = self.real_methods['delete_many'](keys)
        self.log[-1].hit = bool(val)
        return val

    @logged
    def set_many(self, dict_mapping, timeout=None):
        return self.real_methods['set_many'](dict_mapping, timeout)
