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
sys.path.insert(0, glob.glob('../thrift/lib/py/build/lib.*')[0])

from downloader import DownloaderService
from downloader.ttypes import *

from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator

from thrift import Thrift
from thrift.transport import TTwisted
from thrift.protocol import TBinaryProtocol

@inlineCallbacks
def main(client):
  r = NetworkRequest("http://www.baidu.com")
  yield client.download(r)
  
  reactor.stop()

if __name__ == '__main__':
    d = ClientCreator(reactor,
                      TTwisted.ThriftClientProtocol,
                      DownloaderService.Client,
                      TBinaryProtocol.TBinaryProtocolFactory(),
                      ).connectTCP("127.0.0.1", 9090)
    d.addCallback(lambda conn: conn.client)
    d.addCallback(main)

    reactor.run()
