"""
Download timeout middleware

See documentation in docs/topics/downloader-middleware.rst
"""

from dscrapy import signals


class DownloadTimeoutMiddleware(object):

    def __init__(self, timeout=180):
        self._timeout = timeout

    @classmethod
    def from_settings(cls, global_settings, global_signals, global_stats):
        o = cls(global_settings['DOWNLOAD_TIMEOUT'])
        global_signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def spider_opened(self, spider):
        self._timeout = getattr(spider, 'download_timeout', self._timeout)

    def process_request(self, request, spider):
        if self._timeout:
            request.meta.setdefault('download_timeout', self._timeout)
