# encoding: UTF-8

"""
这里的Demo是一个最简单的双均线策略实现
"""

from __future__ import division
from vnpy.trader.app.ctaStrategy.ctaTemplate import (CtaTemplate,
                                                     BarGenerator,
                                                     ArrayManager)
from base.Status import Status
from base.MutilEMaStrategyBase import MutilEMaStrategyBase

########################################################################
class MutilEMaStrategy(CtaTemplate):
    """双指数均线策略Demo"""
    className = 'MutilEMaStrategy'
    author = u'jacklaiu@qq.com'

    # 策略参数
    fastWindow = 5  # 快速均线参数
    slowWindow = 10  # 慢速均线参数
    initDays = 30  # 初始化数据所用的天数

    # 策略变量
    fastMa0 = None  # 当前最新的快速EMA
    fastMa1 = None  # 上一根的快速EMA

    slowMa0 = None
    slowMa1 = None

    # 参数列表，保存了参数的名称
    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol',
                 'fastWindow',
                 'slowWindow']

    # 变量列表，保存了变量的名称
    varList = ['inited',
               'trading',
               'pos',
               'fastMa0',
               'fastMa1',
               'slowMa0',
               'slowMa1']

    # 同步列表，保存了需要保存到数据库的变量名称
    syncList = ['pos']

    # ----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):

        # """Constructor"""
        super(MutilEMaStrategy, self).__init__(ctaEngine, setting)
        #
        self.bg = BarGenerator(self.onBar)
        self.am = ArrayManager()
        #
        # # 注意策略类中的可变对象属性（通常是list和dict等），在策略初始化时需要重新创建，
        # # 否则会出现多个策略实例之间数据共享的情况，有可能导致潜在的策略逻辑错误风险，
        # # 策略类中的这些可变对象属性可以选择不写，全都放在__init__下面，写主要是为了阅读
        # # 策略时方便（更多是个编程习惯的选择）
        self.security = 'RB1901.XSGE'
        self.pricePosi_top = 0
        self.pricePosi_bot = 4
        self.status = Status()
        self.tick = None
        self.strategyBase = MutilEMaStrategyBase(security=self.security, status=self.status,
            maxPosition=4, ctaTemplate=self, enableTrade=True)

    # ----------------------------------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.writeCtaLog(u'多重EMA策略初始化')
        self.putEvent()

    # ----------------------------------------------------------------------
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.writeCtaLog(u'多重EMA策略启动')
        self.putEvent()

    # ----------------------------------------------------------------------
    def onStop(self):
        """停止策略（必须由用户继承实现）"""
        self.writeCtaLog(u'多重EMA策略停止')
        self.putEvent()

    # ----------------------------------------------------------------------
    def onTick(self, tick):
        """收到行情TICK推送（必须由用户继承实现）"""
        self.bg.updateTick(tick)
        self.tick = tick
        if self.strategyBase.startJudgeAndRefreshStatus():
            self.strategyBase.trade(tick)
            self.putEvent()

    # ----------------------------------------------------------------------
    def onBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""
        # 发出状态更新事件
        self.putEvent()

    # ----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass

    # ----------------------------------------------------------------------
    def onTrade(self, trade):
        """收到成交推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass

    # ----------------------------------------------------------------------
    def onStopOrder(self, so):
        """停止单推送"""
        pass
