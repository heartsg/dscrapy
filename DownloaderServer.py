#!/usr/bin/env python

#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#

import sys, glob
sys.path.append('gen-py.twisted')
sys.path.append('/home/hearts/source/dscrapy/')
sys.path.insert(0, glob.glob('../thrift/lib/py/build/lib.*')[0])

from downloader import DownloaderService
from downloader.ttypes import *

from zope.interface import implements
from twisted.internet import reactor

from thrift.transport import TTwisted
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from dscrapy.settings import DScrapySettings
from dscrapy.signalmanager import SignalManager
from dscrapy.utils.misc import load_object
from dscrapy.downloader import Downloader
from dscrapy.http import Request

class DownloaderHandler:
  implements(DownloaderService.Iface)  
  def __init__(self, downloader):
    self.log = {}
    self.downloader = downloader

  def download(self, r):
    print 'download( %s )' % (r.url)
    request = Request(r.url)
    self.downloader.fetch(request, None)

if __name__ == '__main__':

    global_settings = DScrapySettings()
    global_signals = SignalManager()
    global_stats = load_object(global_settings['STATS_CLASS'])(global_settings)
    
    downloader = Downloader(global_settings, global_signals, global_stats)

    handler = DownloaderHandler(downloader)
    processor = DownloaderService.Processor(handler)
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = reactor.listenTCP(9090,
                TTwisted.ThriftServerFactory(processor,
                pfactory), interface="127.0.0.1")
    reactor.run()

