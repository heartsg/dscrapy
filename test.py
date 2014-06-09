import sys
sys.path.append('/home/hearts/source/dscrapy/')


from twisted.internet import reactor

from dscrapy.settings import DScrapySettings
from dscrapy.signalmanager import SignalManager
from dscrapy.downloader import Downloader
from dscrapy.http import Request
from dscrapy.utils.misc import load_object

global_settings = DScrapySettings()
global_signals = SignalManager()
global_stats = load_object(global_settings['STATS_CLASS'])(global_settings)

downloader = Downloader(global_settings, global_signals, global_stats)

request = Request("http://www.baidu.com")
deferred, c1, c2, c3 = downloader.download(request, None)

print c1
print c2
print c3

reactor.run()
