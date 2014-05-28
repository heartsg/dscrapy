"""Download handlers for different schemes"""

from twisted.internet import defer
from dscrapy.exceptions import NotSupported, NotConfigured
from dscrapy.utils.httpobj import urlparse_cached
from dscrapy.utils.misc import load_object
from dscrapy import signals


class DownloadHandlers(object):

    def __init__(self, global_settings, global_signals):
        self._handlers = {}
        self._notconfigured = {}
        handlers = global_settings.get('DOWNLOAD_HANDLERS_BASE')
        handlers.update(global_settings.get('DOWNLOAD_HANDLERS', {}))
        for scheme, clspath in handlers.iteritems():
            # Allow to disable a handler just like any other
            # component (extension, middleware, etc).
            if clspath is None:
                continue
            cls = load_object(clspath)
            try:
                dh = cls(global_settings)
            except NotConfigured as ex:
                self._notconfigured[scheme] = str(ex)
            else:
                self._handlers[scheme] = dh

        global_signals.connect(self._close, signals.engine_stopped)

    def download_request(self, request, spider):
        scheme = urlparse_cached(request).scheme
        try:
            handler = self._handlers[scheme].download_request
        except KeyError:
            msg = self._notconfigured.get(scheme, \
                    'no handler available for that scheme')
            raise NotSupported("Unsupported URL scheme '%s': %s" % (scheme, msg))
        return handler(request, spider)

    @defer.inlineCallbacks
    def _close(self, *_a, **_kw):
        for dh in self._handlers.values():
            if hasattr(dh, 'close'):
                yield dh.close()
