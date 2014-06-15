import os
import json
from os.path import join, exists

from queuelib import PriorityQueue
from scrapy.utils.reqser import request_to_dict, request_from_dict
from scrapy.utils.misc import load_object
from scrapy.utils.job import job_dir
from scrapy import log
from dscrapy.utils.httpobj import urlparse_cached


class Slot(object):

    def __init__(self, key, scheduler):
        self.scheduler = scheduler
        self.df = scheduler.dupefilter
        self.dqdir = self._dqdir(scheduler.jobdir, key)
        self.dqclass = scheduler.dqclass
        self.mqclass = scheduler.mqclass
        self.logunser = scheduler.logunser
        self.stats = scheduler.stats
        self.total_concurrency = scheduler.total_concurrency
        self.domain_concurrency = scheduler.domain_concurrency
        self.ip_concurrency = scheduler.ip_concurrency
        self.spider = None
        self.mqs = PriorityQueue(self._newmq)
        self.dqs = self._dq() if self.dqdir else None
        return self.df.open()

    def close(self, reason):
        if self.dqs:
            prios = self.dqs.close()
            with open(join(self.dqdir, 'active.json'), 'w') as f:
                json.dump(prios, f)
        return self.df.close(reason)

    def has_pending_requests(self):
        return len(self) > 0

    def enqueue_request(self, request):
        if not request.dont_filter and self.df.request_seen(request):
            self.df.log(request, self.spider)
            return
        dqok = self._dqpush(request)
        if dqok:
            self.stats.inc_value('scheduler/enqueued/disk', spider=self.spider)
        else:
            self._mqpush(request)
            self.stats.inc_value('scheduler/enqueued/memory', spider=self.spider)
        self.stats.inc_value('scheduler/enqueued', spider=self.spider)

        return len(self)

    def next_request(self):
        request = self.mqs.pop()
        if request:
            self.stats.inc_value('scheduler/dequeued/memory', spider=self.spider)
        else:
            request = self._dqpop()
            if request:
                self.stats.inc_value('scheduler/dequeued/disk', spider=self.spider)
        if request:
            self.stats.inc_value('scheduler/dequeued', spider=self.spider)
        return request

    def __len__(self):
        return len(self.dqs) + len(self.mqs) if self.dqs else len(self.mqs)

    def _dqpush(self, request):
        if self.dqs is None:
            return
        try:
            reqd = request_to_dict(request, self.spider)
            self.dqs.push(reqd, -request.meta['priority'])
        except ValueError as e: # non serializable request
            if self.logunser:
                log.msg(format="Unable to serialize request: %(request)s - reason: %(reason)s",
                        level=log.ERROR, spider=self.spider,
                        request=request, reason=e)
            return
        else:
            return True

    def _mqpush(self, request):
        self.mqs.push(request, -request.meta['priority'])

    def _dqpop(self):
        if self.dqs:
            d = self.dqs.pop()
            if d:
                return request_from_dict(d, self.spider)

    def _newmq(self, priority):
        return self.mqclass()

    def _newdq(self, priority):
        return self.dqclass(join(self.dqdir, 'p%s' % priority))

    def _dq(self):
        activef = join(self.dqdir, 'active.json')
        if exists(activef):
            with open(activef) as f:
                priiios = json.load(f)
        else:
            prios = ()
        q = PriorityQueue(self._newdq, startprios=prios)
        if q:
            log.msg(format="Resuming crawl (%(queuesize)d requests scheduled)",
                    spider=self.spider, queuesize=len(q))
        return q

    def _dqdir(self, jobdir, key):
        if jobdir:
            dqdir = join(jobdir, 'requests.queue.%s'%key)
            if not exists(dqdir):
                os.makedirs(dqdir)
            return dqdir

class Scheduler(object):

    def __init__(self, dupefilter, jobdir=None, dqclass=None, mqclass=None, logunser=False, stats=None, total_concurrency=0, domain_concurrency=0, ip_concurrency=0):
        self.df = dupefilter
        self.jobdir = jobdir
        self.dqclass = dqclass
        self.mqclass = mqclass
        self.logunser = logunser
        self.stats = stats
        self.slots = {}
        self.total_concurrency = total_concurrency
        self.domain_concurrency = domain_concurrency
        self.ip_concurrency = ip_concurrency

    @classmethod
    def from_settings(cls, global_settings, global_stats):
        settings = global_settings
        dupefilter_cls = load_object(settings['DUPEFILTER_CLASS'])
        dupefilter = dupefilter_cls.from_settings(settings)
        dqclass = load_object(settings['SCHEDULER_DISK_QUEUE'])
        mqclass = load_object(settings['SCHEDULER_MEMORY_QUEUE'])
        logunser = settings.getbool('LOG_UNSERIALIZABLE_REQUESTS')
        total_concurrency = self.settings.getint('CONCURRENT_REQUESTS')
        domain_concurrency = self.settings.getint('CONCURRENT_REQUESTS_PER_DOMAIN')
        ip_concurrency = self.settings.getint('CONCURRENT_REQUESTS_PER_IP')

        return cls(dupefilter, job_dir(settings), dqclass, mqclass, logunser, global_stats, total_concurrency, domain_concurrency, ip_concurrency)

    def enque_request(self, request):
        key, slot = self._get_slot(request)
        return slot.enque_request(request)

    def _get_slot(self, request):
        key = self._get_slot_key(request, spider)
        if key not in self.slots:
            self.slots[key] = Slot(key, self)

        return key, self.slots[key]

    def _get_slot_key(self, request, spider):
        if 'key' in request.meta:
            return request.meta['key']

        key = urlparse_cached(request).hostname or ''

        return key
