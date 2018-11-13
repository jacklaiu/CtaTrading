# encoding: UTF-8

import jqdatasdk
import numpy as np
import time
import talib
from Status import Status
import math

class MutilEMaStrategyBase:

    def __init__(self, security='RB8888.XSGE', status=Status(), ctaTemplate=None, maxPosition=2, enableTrade=False,
                 dayStartTime='09:00:00', dayEndTime='11:30:00', nightStartTime='21:00:00', nightEndTime='23:00:00'):
        self.isTesting = True
        self.enableTrade = enableTrade
        self.ctaTemplate = ctaTemplate
        self.status = status
        self.jqDataAccount = '13824472562'
        self.jqDataPassword = '472562'
        self.frequency = '5m'
        self.dataRow = 100
        self.pricePosi_top = 0
        self.pricePosi_bottom = 4
        self.lastExeTime = None
        self.security = security
        self.pricePositions = []
        self.maxPosition = math.floor(maxPosition / 2) * 2 # 保证双数，可以完全锁仓。
        self.isFirstTrade = True

        self.duo_position = 0 # 多单持仓手数
        self.kong_position = 0 # 空单持仓手数

        self.dayStartTime = dayStartTime
        self.dayEndTime = dayEndTime
        self.nightStartTime = nightStartTime
        self.nightEndTime = nightEndTime

    def _isTradingTime(self):
        if self.isTesting is True:
            return True
        now = time.strftime('%H:%M:%S',time.localtime(time.time()))
        if now > self.dayStartTime and now < self.dayEndTime:
            return True
        if now > self.nightStartTime and now < self.nightEndTime:
            return True
        return False

    def _shouldStartJudge(self):
        currentTimestamp = time.time() * 1000
        isTradingTime = self._isTradingTime()
        frequencyLimitFlag = int(time.strftime('%M', time.localtime(time.time()))) % int(self.frequency[0:-1]) == 0
        if isTradingTime is True and self.lastExeTime is None: # 第一次
            if frequencyLimitFlag is True:
                self.lastExeTime = currentTimestamp
                return True
            else:
                return False
        if isTradingTime is True and currentTimestamp - self.lastExeTime > 66 * 1000: # 当前时间已经距离上次调用更新状态过了self.waittime分钟，可以再次调用
            if frequencyLimitFlag is True:
                self.lastExeTime = currentTimestamp
                return True
            else:
                return False
        return False

    def startJudgeAndRefreshStatus(self, currentTimeForTesting=None):
        self.pricePositions = []
        if self._shouldStartJudge() is False:
            return False
        jqdatasdk.auth(self.jqDataAccount, self.jqDataPassword)
        nowTimeString = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        if currentTimeForTesting is not None:
            nowTimeString = currentTimeForTesting
        self.df = jqdatasdk.get_price(security=self.security, count=self.dataRow, end_date=nowTimeString, frequency=self.frequency,
                                      fields=['close'])
        close = [float(x) for x in self.df['close']]
        self.df['EMA5'] = talib.EMA(np.array(close), timeperiod=5)
        self.df['EMA10'] = talib.EMA(np.array(close), timeperiod=10)
        self.df['EMA20'] = talib.EMA(np.array(close), timeperiod=20)
        self.df['EMA40'] = talib.EMA(np.array(close), timeperiod=40)
        self.df['EMA60'] = talib.EMA(np.array(close), timeperiod=60)
        self.indexList = self.df[self.df.EMA60 == self.df.EMA60].index.tolist()
        for index in self.indexList:
            ema5 = self.df.loc[index, 'EMA5']
            emas = sorted(
                [ema5, self.df.loc[index, 'EMA10'], self.df.loc[index, 'EMA20'], self.df.loc[index, 'EMA40'], self.df.loc[index, 'EMA60']],
                reverse=True)
            pricePosi = 0
            for ema in emas:
                if ema == ema5:
                    break
                pricePosi = pricePosi + 1

            self.pricePositions.append(pricePosi)

        self._refreshStatus()
        return True

    def _refreshStatus(self): # lockingbuy lockingshort holdingbuy holdingshort waiting
        df = self.df
        count = 0
        for pricePosi in self.pricePositions:
            _status = self.status.status
            _buyStartClose = self.status.buyStartClose
            _shortStartClose = self.status.shortStartClose
            _lockClose = self.status.lockClose
            try:
                index = self.indexList[count]
            except:
                print

            price = df.loc[index, 'close']


            # status == waiting不会触发状态
            if self.status.status == 'holdingbuy' or self.status.status == 'holdingshort' or self.status.status == 'lockingbuy' or self.status.status == 'lockingshort':

                if self.status.status == 'holdingbuy' or self.status.status == 'lockingbuy':
                    # 平仓点
                    if pricePosi > self.pricePosi_top:
                        self.status.lockClose = 0
                        self.status.buyStartClose = 0
                        self.status.shortStartClose = 0
                        self.status.preStatus = self.status.status
                        self.status.status = 'waiting'

                    if self.status.status == 'holdingbuy':
                        if price < self.status.buyStartClose:# 当前holdingbuy，价格比开仓价格低，开始亏损，执行锁仓
                            self.status.lockClose = price
                            # self.status.buyStartClose = buyStartClose
                            self.status.shortStartClose = 0
                            self.status.preStatus = self.status.status
                            self.status.status = 'lockingbuy'

                    elif self.status.status == 'lockingbuy':
                        if price > self.status.buyStartClose:
                            self.status.lockClose = 0
                            # self.status.buyStartClose = buyStartClose
                            self.status.shortStartClose = 0
                            self.status.preStatus = self.status.status
                            self.status.status = 'holdingbuy'



                elif self.status.status == 'holdingshort' or self.status.status == 'lockingshort':

                    # 平仓点
                    if pricePosi < self.pricePosi_bottom:
                        self.status.lockClose = 0
                        self.status.buyStartClose = 0
                        self.status.shortStartClose = 0
                        self.status.preStatus = self.status.status
                        self.status.status = 'waiting'

                    if self.status.status == 'holdingshort':
                        if price > self.status.shortStartClose: # 当前holdingshort，价格比开仓价格高，开始亏损，执行锁仓
                            self.status.lockClose = price
                            self.status.buyStartClose = 0
                            # self.status.shortStartClose = shortStartClose
                            self.status.preStatus = self.status.status
                            self.status.status = 'lockingshort'

                    elif self.status.status == 'lockingshort':
                        if price < self.status.shortStartClose:# 当前lockingshort，价格比开仓价格低，停止亏损，取消锁仓
                            self.status.lockClose = 0
                            self.status.buyStartClose = 0
                            # self.status.shortStartClose = shortStartClose
                            self.status.preStatus = self.status.status
                            self.status.status = 'holdingshort'

                count = count + 1
                continue

            # 开多仓
            if pricePosi == 0:
                self.status.lockClose = 0
                self.status.buyStartClose = price
                self.status.shortStartClose = 0
                self.status.preStatus = self.status.status
                self.status.status = 'holdingbuy'

            # 开空仓
            if pricePosi == 4:
                self.status.lockClose = 0
                self.status.buyStartClose = 0
                self.status.shortStartClose = price
                self.status.preStatus = self.status.status
                self.status.status = 'holdingshort'

            count = count + 1

        self.ctaTemplate.writeCtaLog('prestatus: ' + self.status.preStatus + ' - status: ' + self.status.status)

    def buy(self, tick):
        preStatus = self.status.preStatus
        status = self.status.status
        if preStatus == 'waiting' and status == 'holdingbuy' and self.isWait() is True and self.isHoldingBuy() is False:
            upLimit = tick.upperLimit
            if self.enableTrade is True:
                self.ctaTemplate.buy(upLimit, self.maxPosition)
            self.ctaTemplate.writeCtaLog(u'开多' + str(self.maxPosition) + '手')
            self.duo_position = self.maxPosition
            self.ctaTemplate.writeCtaLog(u'多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            return True
        return False

    def short(self, tick):
        preStatus = self.status.preStatus
        status = self.status.status
        if preStatus == 'waiting' and status == 'holdingshort' and self.isWait() is True and self.isHoldingShort() is False:
            downLimit = tick.lowerLimit
            if self.enableTrade is True:
                self.ctaTemplate.short(downLimit, self.maxPosition)
            self.ctaTemplate.writeCtaLog(u'开空' + str(self.maxPosition) + '手')
            self.kong_position = self.maxPosition
            self.ctaTemplate.writeCtaLog(u'多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            return True
        return False

    def closePosition(self, tick):
        preStatus = self.status.preStatus
        status = self.status.status
        upLimit = tick.upperLimit
        downLimit = tick.lowerLimit

        if preStatus == 'holdingbuy' and status == 'waiting' and self.isWait() is False and self.isHoldingBuy() is True:# 平多
            if self.enableTrade is True:
                self.ctaTemplate.sell(downLimit, self.maxPosition)
            self.ctaTemplate.writeCtaLog(u'平多' + str(self.maxPosition) + '手')
            self.duo_position = 0
            self.ctaTemplate.writeCtaLog(u'多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))

        if preStatus == 'holdingshort' and status == 'waiting' and self.isWait() is False and self.isHoldingShort() is True:# 平空
            if self.enableTrade is True:
                self.ctaTemplate.cover(upLimit, self.maxPosition)
            self.ctaTemplate.writeCtaLog(u'平空' + str(self.maxPosition) + '手')
            self.kong_position = 0
            self.ctaTemplate.writeCtaLog(u'多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))

        if (preStatus == 'lockingbuy' or preStatus == 'lockingshort') and status == 'waiting' and self.isLock() is True and self.isWait() is False: # 双平
            if self.enableTrade is True:
                self.ctaTemplate.sell(downLimit, self.maxPosition / 2)
                self.ctaTemplate.cover(upLimit, self.maxPosition / 2)
            self.ctaTemplate.writeCtaLog(u'双平' + str(self.maxPosition / 2) + '手')
            self.duo_position = 0
            self.kong_position = 0
            self.ctaTemplate.writeCtaLog(u'多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))

    def lock(self, tick):
        preStatus = self.status.preStatus
        status = self.status.status
        upLimit = tick.upperLimit
        downLimit = tick.lowerLimit

        if preStatus == 'holdingbuy' and status == 'lockingbuy' and self.isLock() is False and self.isHoldingBuy() is True: # 锁多仓
            if self.enableTrade is True:
                self.ctaTemplate.sell(downLimit, self.maxPosition / 2)
                self.ctaTemplate.short(downLimit, self.maxPosition / 2)
            self.ctaTemplate.writeCtaLog(u'锁多' + str(self.maxPosition / 2) + '手')
            self.duo_position = self.duo_position / 2
            self.kong_position = self.duo_position / 2
            self.ctaTemplate.writeCtaLog(u'多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))

        if preStatus == 'holdingshort' and status == 'lockingshort' and self.isLock() is False and self.isHoldingShort() is True: # 锁空仓
            if self.enableTrade is True:
                self.ctaTemplate.cover(upLimit, self.maxPosition / 2)
                self.ctaTemplate.buy(upLimit, self.maxPosition / 2)
            self.ctaTemplate.writeCtaLog(u'锁空' + str(self.maxPosition / 2) + '手')
            self.duo_position = self.duo_position / 2
            self.kong_position = self.duo_position / 2
            self.ctaTemplate.writeCtaLog(u'多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))

    def unlock(self, tick):
        preStatus = self.status.preStatus
        status = self.status.status
        upLimit = tick.upperLimit
        downLimit = tick.lowerLimit
        if preStatus == 'lockingbuy' and status == 'holdingbuy' and self.isLock() is True:
            if self.enableTrade is True:
                self.ctaTemplate.cover(upLimit, self.maxPosition / 2)
                self.ctaTemplate.buy(upLimit, self.maxPosition / 2)
            self.ctaTemplate.writeCtaLog(u'解多锁' + str(self.maxPosition / 2) + '手')
            self.duo_position = self.maxPosition
            self.kong_position = 0
            self.ctaTemplate.writeCtaLog(u'多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
        if preStatus == 'lockingshort' and status == 'holdingshort' and self.isLock() is True:
            if self.enableTrade is True:
                self.ctaTemplate.sell(downLimit, self.maxPosition / 2)
                self.ctaTemplate.short(downLimit, self.maxPosition / 2)
            self.ctaTemplate.writeCtaLog(u'解空锁' + str(self.maxPosition / 2) + '手')
            self.duo_position = 0
            self.kong_position = self.maxPosition
            self.ctaTemplate.writeCtaLog(u'多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))

    def trade(self, tick):
        if self.isFirstTrade is True:
            self.status.preStatus = 'waiting'
            hadBuy = self.buy(tick)
            hadShort = self.short(tick)
            if hadBuy == True or hadShort == True:
                self.isFirstTrade = False
        else:
            self.buy(tick)
            self.short(tick)
            self.closePosition(tick)
            self.lock(tick)
            self.unlock(tick)
        self.ctaTemplate.putEvent()

    def isLock(self):
        duo = self.duo_position
        kon = self.kong_position
        if duo == kon:
            return True
        else:
            return False

    def isWait(self):
        duo = self.duo_position
        kon = self.kong_position
        if duo == 0 and kon == 0:
            return True
        return False

    def isHoldingBuy(self):
        duo = self.duo_position
        max = self.maxPosition
        if duo == max:
            return True
        return False

    def isHoldingShort(self):
        kon = self.kong_position
        max = self.maxPosition
        if kon == max:
            return True
        return False

