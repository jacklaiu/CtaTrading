
import datetime
from base.MutilEMaStrategyBase import MutilEMaStrategyBase
from base.Status import Status
import base.Util as util

security = 'RB9999.XSGE' #'FG9999.XZCE' 'RB9999.XSGE' 'JM9999.XDCE'
pricePosi_top = 0
pricePosi_bot = 4
status = Status()
tick = None
jqDataAccount = '13268108673'#'13268108673' '13824472562'
jqDataPassword = 'king20110713'#'king20110713' '472562'
frequency = '5m'
strategyBase = MutilEMaStrategyBase(security=security, status=status, ctaTemplate=None, enableTrade=False,
                                    frequency=frequency,
                                    jqDataAccount=jqDataAccount, jqDataPassword=jqDataPassword)
times = util.getTimeSerial('2018-11-19 09:00:00', count=1000*80, periodSec=12)
for t in times:
    if strategyBase.startJudgeAndRefreshStatus(t):
        strategyBase.trade(None)
