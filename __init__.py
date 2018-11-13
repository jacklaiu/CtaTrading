
import datetime
from base.MutilEMaStrategyBase import MutilEMaStrategyBase
from base.Status import Status
import base.Util as util

security = 'RB1901.XSGE'
pricePosi_top = 0
pricePosi_bot = 4
status = Status()
tick = None
strategyBase = MutilEMaStrategyBase(security=security, status=status, maxPosition=2, ctaTemplate=None, enableTrade=False)
times = util.getTimeSerial('2018-11-05 22:00:00', count=1000*20, periodSec=12)
for t in times:
    if strategyBase.startJudgeAndRefreshStatus(t):
        strategyBase.trade(None)
