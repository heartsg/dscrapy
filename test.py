import sys
sys.path.append('/home/hearts/source/dscrapy/')


from twisted.internet import reactor

from dscrapy.settings import DScrapySettings
from dscrapy.signalmanager import SignalManager
from dscrapy.downloader import Downloader
from dscrapy.http import Request

global_settings = DScrapySettings()
global_signals = SignalManager()
downloader = Downloader(global_settings, global_signals)

request = Request("http://www.baidu.com")
downloader.fetch(request, None)

reactor.run()
