"""
DefaultHeaders downloader middleware

See documentation in docs/topics/downloader-middleware.rst
"""


class DefaultHeadersMiddleware(object):

    def __init__(self, headers):
        self._headers = headers

    @classmethod
    def from_settings(cls, global_settings, global_signals, global_stats):
        return cls(global_settings.get('DEFAULT_REQUEST_HEADERS').items())

    def process_request(self, request, spider):
        for k, v in self._headers:
            request.headers.setdefault(k, v)
