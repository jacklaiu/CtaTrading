### coding: utf8
from numpy import int32

RiskControlRate = -0.2

class ControlRisk():

    def __init__(self, ctaEngine, maxPosition):
        self.ctaEngine = ctaEngine
        self.maxPosition = maxPosition
        self.realOpenKonPrice = None
        self.realOpenDuoPrice = None

    def setOpenDuoPrice(self, price):
        self.realOpenDuoPrice = price

    def setOpenKonPrice(self, price):
        self.realOpenKonPrice = price

    def releaseAll(self):
        self.realOpenKonPrice = None
        self.realOpenDuoPrice = None

    def controlOnTick(self, tick):
        # 持有多仓风控计算实时盈亏
        if self.realOpenKonPrice is not None:
            openPrice = self.realOpenKonPrice
            rate = round((openPrice - tick.lastPrice) / openPrice, 8) * 100
            if rate < RiskControlRate:
                self.lockKon = True
                self.lockActionToken = True
            if self.locking is True and rate > -RiskControlRate:
                self.lockKon = False
                self.unlockActionToken = True

        # 持有空仓风控计算实时盈亏
        if self.realOpenDuoPrice is not None:
            openPrice = self.realOpenDuoPrice
            rate = round((tick.lastPrice - openPrice) / openPrice, 8) * 100
            if rate < RiskControlRate:
                self.lockDuo = True
                self.lockActionToken = True
            if self.locking is True and rate > -RiskControlRate:
                self.lockDuo = False
                self.unlockActionToken = True

        if self.realOpenDuoPrice is None and self.realOpenKonPrice is None:
            return
        openPrice = self.realOpenDuoPrice
        rate = round((tick.lastPrice - openPrice) / openPrice, 8) * 100
        # 锁动作执行
        if self.lockActionToken is True and self.locking is False:
            if self.realOpenKonPrice is not None:
                print "lockKon rate: " + str(rate)
                if self.ctaEngine is not None: self.ctaEngine.cover(tick.upperLimit * 0.995,
                           int32(self.maxPosition))  # 平空!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if self.realOpenDuoPrice is not None:
                print "lockDuo rate: " + str(rate)
                if self.ctaEngine is not None: self.ctaEngine.sell(tick.lowerLimit * 0.995,
                          int32(self.maxPosition))  # 平多!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            self.locking = True
            self.lockActionToken = False

        # 解锁动作执行
        if self.unlockActionToken is True and self.locking is True:
            if self.realOpenKonPrice is not None:
                print "unlockKon rate: " + str(rate)
                if self.ctaEngine is not None: self.ctaEngine.short(tick.lowerLimit * 0.995,
                           int32(self.maxPosition))  # 开空!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if self.realOpenDuoPrice is not None:
                print "unlockDuo rate: " + str(rate)
                if self.ctaEngine is not None: self.ctaEngine.buy(tick.upperLimit * 0.995,
                         int32(self.maxPosition))  # 开多!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            self.locking = False
            self.unlockActionToken = False

        # 拒绝在没有大利润的前提下隔夜持仓
