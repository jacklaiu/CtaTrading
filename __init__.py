
import datetime
from base.MutilEMaStrategyBase import MutilEMaStrategyBase
from base.Status import Status
import base.Util as util

security = 'RB1901.XSGE'
pricePosi_top = 0
pricePosi_bot = 4
status = Status()
tick = None
strategyBase = MutilEMaStrategyBase(security=security, status=status, maxPosition=2, ctaTemplate=None, enableTrade=False, isTesting=True)
times = util.getTimeSerial('2018-11-13 09:00:00', count=1*60*60, periodSec=30)
for t in times:
    if strategyBase.startJudgeAndRefreshStatus(t):
        strategyBase.trade(None)
