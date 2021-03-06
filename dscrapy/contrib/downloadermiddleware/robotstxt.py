"""
This is a middleware to respect robots.txt policies. To activate it you must
enable this middleware and enable the ROBOTSTXT_OBEY setting.

"""

import robotparser

from dscrapy import signals, log
from dscrapy.exceptions import NotConfigured, IgnoreRequest
from dscrapy.http import Request
from dscrapy.utils.httpobj import urlparse_cached


class RobotsTxtMiddleware(object):
    DOWNLOAD_PRIORITY = 1000

    def __init__(self, global_settings, crawler=None):
        if not global_settings.getbool('ROBOTSTXT_OBEY'):
            raise NotConfigured

        self.crawler = crawler
        self._useragent = global_settings.get('USER_AGENT')
        self._parsers = {}
        self._spider_netlocs = set()

    @classmethod
    def from_settings(cls, global_settings, global_signals, global_stats):
        return cls(global_settings)

    def process_request(self, request, spider):
        useragent = self._useragent
        rp = self.robot_parser(request, spider)
        if rp and not rp.can_fetch(useragent, request.url):
            log.msg(format="Forbidden by robots.txt: %(request)s",
                    level=log.DEBUG, request=request)
            raise IgnoreRequest

    def robot_parser(self, request, spider):
        url = urlparse_cached(request)
        netloc = url.netloc
        if netloc not in self._parsers:
            self._parsers[netloc] = None
            robotsurl = "%s://%s/robots.txt" % (url.scheme, url.netloc)
            robotsreq = Request(robotsurl, priority=self.DOWNLOAD_PRIORITY)
            dfd = self.crawler.engine.download(robotsreq, spider)
            dfd.addCallback(self._parse_robots)
            self._spider_netlocs.add(netloc)
        return self._parsers[netloc]

    def _parse_robots(self, response):
        rp = robotparser.RobotFileParser(response.url)
        rp.parse(response.body.splitlines())
        self._parsers[urlparse_cached(response).netloc] = rp
