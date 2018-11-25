# encoding: UTF-8

import jqdatasdk
import numpy as np
import time
import talib
from Status import Status
import math
import Util as util
from numpy import int32
import Dao as dao
from judgement.Master import Judgement_Master as jm

class MutilEMaStrategyBase:

    def __init__(self, security='RB1901.XSGE', status=Status(), ctaTemplate=None, enableTrade=False,
                 frequency='5m',
                 dayStartTime='09:00:20', dayEndTime='10:14:00',
                 noonStartTime='10:30:00', noonEndTime='11:29:00',
                 afternoonStartTime='13:30:00', afternoonEndTime='14:59:00',
                 nightStartTime='21:00:00', nightEndTime='22:59:00',
                 jqDataAccount='13268108673', jqDataPassword='king20110713'):
        self.enableTrade = enableTrade
        self.ctaTemplate = ctaTemplate
        self.status = status
        self.jqDataAccount = jqDataAccount
        self.jqDataPassword = jqDataPassword
        # self.jqDataAccount = '13824472562'
        # self.jqDataPassword = '472562'
        self.frequency = frequency
        self.dataRow = 300
        self.pricePosi_top = 0
        self.pricePosi_bottom = 4
        self.lastExeTime = None
        self.security = security
        self.pricePositions = []
        self.maxPosition = math.floor(dao.readMaxPosition(security) / 2) * 2 # 保证双数，可以完全锁仓。
        self.duo_position = dao.readDuoPosition(security) # 多单持仓手数
        self.kong_position = dao.readKongPosition(security) # 空单持仓手数

        self.jm = jm(self)

        self.lastestAbsK = None

        self.writeCtaLog('########################允许交易：' + str(self.enableTrade))
        self.writeCtaLog('########################合约代码：' + str(self.security))
        self.writeCtaLog('########################多单持仓：' + str(self.duo_position))
        self.writeCtaLog('########################空单持仓：' + str(self.kong_position))
        self.writeCtaLog('########################最大持仓：' + str(self.maxPosition))
        self.writeCtaLog('########################策略级别：' + str(self.frequency))
        self.writeCtaLog('########################jqdata账号：' + str(self.jqDataAccount))

        self.dayStartTime = dayStartTime
        self.dayEndTime = dayEndTime
        self.noonStartTime = noonStartTime
        self.noonEndTime = noonEndTime
        self.afternoonStartTime = afternoonStartTime
        self.afternoonEndTime = afternoonEndTime
        self.nightStartTime = nightStartTime
        self.nightEndTime = nightEndTime

    def _isTradingTime(self, currentTimeForTesting):
        if currentTimeForTesting is None:
            now = time.strftime('%H:%M:%S',time.localtime(time.time()))
        else:
            ts = util.string2timestamp(currentTimeForTesting)
            now = time.strftime('%H:%M:%S', time.localtime(ts))
        if now >= self.dayStartTime and now <= self.dayEndTime:
            return True
        if now >= self.afternoonStartTime and now <= self.afternoonEndTime:
            return True
        if now >= self.noonStartTime and now <= self.noonEndTime:
            return True
        if now >= self.nightStartTime and now <= self.nightEndTime:
            return True
        return False

    def _shouldStartJudge(self, currentTimeForTesting=None):
        currentTimestamp = time.time() * 1000
        isTradingTime = self._isTradingTime(currentTimeForTesting)
        if currentTimeForTesting is not None:
            ts  = util.string2timestamp(currentTimeForTesting)
            frequencyLimitFlag = int(time.strftime('%M', time.localtime(ts))) % int(self.frequency[0:-1]) == 0
            currentTimestamp = util.string2timestamp(currentTimeForTesting) * 1000
        else:
            n = int(time.strftime('%M', time.localtime(currentTimestamp/1000))) % int(self.frequency[0:-1])
            frequencyLimitFlag = n == 0

        if isTradingTime is True and self.lastExeTime is None: # 第一次
            if frequencyLimitFlag is True:
                self.lastExeTime = currentTimestamp
                return True
            else:
                return False

        elif isTradingTime is True and currentTimestamp - self.lastExeTime > 66 * 1000: # 当前时间已经距离上次调用更新状态过了self.waittime分钟，可以再次调用
            if frequencyLimitFlag is True:
                self.lastExeTime = currentTimestamp
                return True
            else:
                return False
        return False

    def startJudgeAndRefreshStatus(self, currentTimeForTesting=None):
        self.pricePositions = []
        self.pricePositions_ema10 = []
        if self._shouldStartJudge(currentTimeForTesting) is False:
            return False
        if self.enableTrade is True:
            time.sleep(19)
        jqdatasdk.auth(self.jqDataAccount, self.jqDataPassword)
        nowTimeString = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        if currentTimeForTesting is not None:
            nowTimeString = currentTimeForTesting

        self.df = jqdatasdk.get_price(
            security=self.security,
            count=self.dataRow,
            end_date=nowTimeString[0:nowTimeString.rindex(':') + 1] + '30',
            frequency=self.frequency,
            fields=['close']
        )
        close = [float(x) for x in self.df['close']]
        self.df['EMA5'] = talib.EMA(np.array(close), timeperiod=5)
        self.df['EMA10'] = talib.EMA(np.array(close), timeperiod=10)
        self.df['EMA20'] = talib.EMA(np.array(close), timeperiod=20)
        self.df['EMA40'] = talib.EMA(np.array(close), timeperiod=40)
        self.df['EMA60'] = talib.EMA(np.array(close), timeperiod=60)
        self.df['EMA120'] = talib.EMA(np.array(close), timeperiod=120)
        self.df['EMA180'] = talib.EMA(np.array(close), timeperiod=180)
        self.df['MA5'] = talib.MA(np.array(close), timeperiod=5)
        self.df['MA10'] = talib.MA(np.array(close), timeperiod=10)
        self.df['MA20'] = talib.MA(np.array(close), timeperiod=20)
        self.df['MA40'] = talib.MA(np.array(close), timeperiod=40)
        self.df['MA60'] = talib.MA(np.array(close), timeperiod=60)
        self.df['MA120'] = talib.MA(np.array(close), timeperiod=120)
        self.df['MA180'] = talib.MA(np.array(close), timeperiod=180)

        self.indexList = self.df[self.df.EMA180 == self.df.EMA180].index.tolist()

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

        self.refreshStatus(nowTimeString)
        return True

    def refreshStatus(self, nowTimeString=None): # lockingbuy lockingshort holdingbuy holdingshort waiting
        # 保证最新的数据是符合frequency的，因为需要保证数据的连续性
        ts = util.string2timestamp(str(self.indexList[-1]))
        frequencyLimitFlag = int(time.strftime('%M', time.localtime(ts))) % int(self.frequency[0:-1]) == 0
        if frequencyLimitFlag is True:
            count = 0
            self.lastestAbsK = None
            for pricePosi in self.pricePositions:
                index = self.indexList[count]
                self.now_ema5 = self.df['EMA5'][index]
                self.now_ema10 = self.df['EMA10'][index]
                self.now_ema20 = self.df['EMA10'][index]
                self.now_pricePosi = pricePosi
                self.now_price = self.df.loc[index, 'close']
                self.doRefresh(count, nowTimeString)
                count = count + 1

        _emak60 = self.getEMAK(ematype='60', preCount=0) * 100
        _emak120 = self.getEMAK(ematype='120', preCount=0) * 100
        _mak120 = self.getMAK(matype='120', preCount=0) * 100
        _emak60_120_dR = (abs(_emak60) - abs(_emak120)) / abs(_emak60)
        self.writeCtaLog('[' + nowTimeString + ']: preStatus: ' + str(self.status.preStatus)
                         + ' -> status(now): ' + self.status.status
                         )
                         # + ' -> emak60 : ' + str(_emak60)
                         # + ' -> mak120: ' + str(_mak120)
                         # + ' -> _emak60_120_dR: ' + str(_emak60_120_dR)
                         # + ' -> pricePosi: ' + str(self.now_pricePosi))

    def doRefresh(self, indexCount, nowTimeString):
        # lemak = 0
        # if count == self.indexList.__len__() - 1:
        #     lemak = self.getLifeEMAK(preCount=(self.indexList.__len__() - count - 1))
        # else:
        #     if count == 0:
        #         lemak = self.getLifeEMAK(preCount=(self.indexList.__len__() - count - 2))
        #     else:
        #         lemak = self.getLifeEMAK(preCount=(self.indexList.__len__() - count - 2))

        # status == waiting不会触发状态
        if self.status.status == 'holdingbuy' or self.status.status == 'holdingshort' or self.status.status == 'lockingbuy' or self.status.status == 'lockingshort':

            # if self.status.status == 'holdingbuy' or self.status.status == 'holdingshort':
            #     self.holdingCount = self.holdingCount + 1

            if self.status.status == 'holdingbuy' or self.status.status == 'lockingbuy':
                # 平仓点
                if self.now_pricePosi > self.pricePosi_top:
                    self.status.lockClose = 0
                    self.status.buyStartClose = 0
                    self.status.shortStartClose = 0
                    self.status.preStatus = self.status.status
                    self.status.status = 'waiting'

            elif self.status.status == 'holdingshort' or self.status.status == 'lockingshort':
                # 平仓点
                if self.now_pricePosi < self.pricePosi_bottom:
                    self.status.lockClose = 0
                    self.status.buyStartClose = 0
                    self.status.shortStartClose = 0
                    self.status.preStatus = self.status.status
                    self.status.status = 'waiting'
        if nowTimeString == '2018-11-13 14:20:00' and indexCount == self.indexList.__len__() - 1:
            print
        emak60 = self.getEMAK(ematype='60', indexCount=indexCount) * 100
        emak120 = self.getEMAK(ematype='120', indexCount=indexCount) * 100
        mak5 = self.getMAK(matype='5', indexCount=indexCount) * 100
        mak120 = self.getMAK(matype='120', indexCount=indexCount) * 100
        mak180 = self.getMAK(matype='180', indexCount=indexCount) * 100
        # 开多仓
        if self.now_pricePosi == self.pricePosi_top \
                and mak5 > 100 \
                and emak60 > 0 \
                and mak120 > 0 \
                and mak180 > 0 \
                and abs(emak60) > abs(emak120) \
                and True:#(abs(emak60) - abs(emak120)) / abs(60) > 0.3:
            self.status.lockClose = 0
            self.status.buyStartClose = self.now_price
            self.status.shortStartClose = 0
            self.status.preStatus = self.status.status
            self.status.status = 'holdingbuy'

        # 开空仓
        if self.now_pricePosi == self.pricePosi_bottom \
                and mak5 < -100 \
                and emak60 < 0 \
                and mak120 < 0 \
                and mak180 < 0 \
                and abs(emak60) > abs(emak120) \
                and True:#(abs(emak60) - abs(emak120)) / abs(60) > 0.3:

            if nowTimeString == '2018-11-13 14:20:00' and indexCount == self.indexList.__len__() - 1:
                print
            self.status.lockClose = 0
            self.status.buyStartClose = 0
            self.status.shortStartClose = self.now_price
            self.status.preStatus = self.status.status
            self.status.status = 'holdingshort'

    def markAbsLifeEMAK(self, indexCount):
        self.lastestAbsK = abs(self.getLifeEMAK(indexCount=indexCount))

    def clearAbsLifeEMAK(self):
        self.lastestAbsK = 0

    def getLifeEMAK(self, preCount=0, indexCount=None):

        if indexCount is not None:
            f = self.getEMAK(ematype='5', indexCount=indexCount)
            t = self.getEMAK(ematype='10', indexCount=indexCount)
            return f + t

        f = self.getEMAK(ematype='5', preCount=preCount)
        t = self.getEMAK(ematype='10', preCount=preCount)
        return f + t

    def getEMADistance(self, ematypes=('5', '10', '20', '40', '60'), preCount=0, indexCount=None):

        if indexCount is not None:
            values = []
            for ematype in ematypes:
                values.append(float(self.df.loc[self.indexList[indexCount], 'EMA' + ematype]))
            preV = None
            firstV = None
            distance = 0
            for value in values:
                if firstV is None:
                    firstV = value
                if preV is not None:
                    distance = distance + abs(value - preV) / ematypes.__len__()
                preV = value
            return round(distance / ematypes.__len__() / firstV, 8) * 100

        values = []
        for ematype in ematypes:
            values.append(float(self.df.loc[self.indexList[-1 - preCount], 'EMA' + ematype]))
        preV = None
        firstV = None
        distance = 0
        for value in values:
            if firstV is None:
                firstV = value
            if preV is not None:
                distance = distance + abs(value - preV) / ematypes.__len__()
            preV = value
        return round(distance / ematypes.__len__() / firstV, 8) * 100

    def getEMAK(self, preCount=0, ematype='5', indexCount=None):

        if indexCount is not None:
            ema_now = float(self.df.loc[self.indexList[indexCount], 'EMA' + ematype])
            if indexCount == 0:
                ema_pre = ema_now
            else:
                ema_pre = float(self.df.loc[self.indexList[indexCount - 1], 'EMA' + ematype])
            banlance = ema_now / 1000
            return (ema_now - ema_pre) / banlance * 3

        ema_1 = float(self.df.loc[self.indexList[-1 - preCount], 'EMA' + ematype])
        a = ema_1 / 1000
        ema_2 = float(self.df.loc[self.indexList[-2 - preCount], 'EMA' + ematype])
        return (ema_1 - ema_2) / a * 3

    def getMAK(self, preCount=0, matype='5', indexCount=None):

        if indexCount is not None:
            ma_now = float(self.df.loc[self.indexList[indexCount], 'MA' + matype])
            if indexCount == 0:
                ma_pre = ma_now
            else:
                ma_pre = float(self.df.loc[self.indexList[indexCount - 1], 'MA' + matype])
            banlance = ma_now / 1000
            return (ma_now - ma_pre) / banlance * 3

        ma_1 = float(self.df.loc[self.indexList[-1 - preCount], 'MA' + matype])
        a = ma_1 / 1000
        ma_2 = float(self.df.loc[self.indexList[-2 - preCount], 'MA' + matype])
        return (ma_1 - ma_2) / a * 3

    def getMAValue(self, matype='5', indexCount=None):
        ma_now = float(self.df.loc[self.indexList[indexCount], 'MA' + matype])
        return ma_now

    def buy(self, tick):
        status = self.status.status
        if status == 'holdingbuy' and self.isWait() is True and self.isHoldingBuy() is False:
            if self.enableTrade is True:
                self.ctaTemplate.buy(tick.upperLimit, int32(self.maxPosition))
            self.writeCtaLog('开多' + str(self.maxPosition) + '手')
            self.duo_position = self.maxPosition
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)
            return True
        return False

    def short(self, tick):
        status = self.status.status
        if status == 'holdingshort' and self.isWait() is True and self.isHoldingShort() is False:
            if self.enableTrade is True:
                self.ctaTemplate.short(tick.lowerLimit, int32(self.maxPosition))
            self.writeCtaLog('开空' + str(self.maxPosition) + '手')
            self.kong_position = self.maxPosition
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)
            return True
        return False

    def closePosition(self, tick):
        status = self.status.status
        if status == 'waiting' and self.isWait() is False and self.isHoldingBuy() is True:
            if self.enableTrade is True:
                self.ctaTemplate.sell(tick.lowerLimit, int32(self.maxPosition)) # 平多
            self.writeCtaLog('平多' + str(self.maxPosition) + '手')
            self.duo_position = 0
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)

        if status == 'waiting' and self.isWait() is False and self.isHoldingShort() is True:
            if self.enableTrade is True:
                self.ctaTemplate.cover(tick.upperLimit, int32(self.maxPosition)) # 平空
            self.writeCtaLog('平空' + str(self.maxPosition) + '手')
            self.kong_position = 0
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)

        if status == 'waiting' and self.isWait() is False: # 双平
            if self.duo_position > 0 and self.isHoldingBuy():
                if self.enableTrade is True:
                    self.ctaTemplate.sell(tick.lowerLimit, int32(self.maxPosition))  # 平多
                self.writeCtaLog('平多' + str(self.maxPosition) + '手')
            if self.kong_position > 0 and self.isHoldingShort():
                if self.enableTrade is True:
                    self.ctaTemplate.cover(tick.upperLimit, int32(self.maxPosition))  # 平空
                self.writeCtaLog('平空' + str(self.maxPosition) + '手')
            self.duo_position = 0
            self.kong_position = 0
            dao.updatePosition(0, 0, self.security)

    def lock(self, tick):
        preStatus = self.status.preStatus
        status = self.status.status

        if preStatus == 'holdingbuy' and status == 'lockingbuy' and self.isHoldingBuy() is True: # 锁多仓
            if self.enableTrade is True:
                self.ctaTemplate.sell(tick.lowerLimit, int32(self.maxPosition))  # 平多
            self.writeCtaLog('平' + str(self.maxPosition) + '手')
            self.duo_position = 0
            self.kong_position = 0
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)

        if preStatus == 'holdingshort' and status == 'lockingshort' and self.isHoldingShort() is True: # 锁空仓
            if self.enableTrade is True:
                self.ctaTemplate.cover(tick.upperLimit, int32(self.maxPosition))  # 平空
            self.writeCtaLog('平' + str(self.maxPosition) + '手')
            self.duo_position = 0
            self.kong_position = 0
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)

    def unlock(self, tick):
        preStatus = self.status.preStatus
        status = self.status.status
        if preStatus == 'lockingbuy' and status == 'holdingbuy' and self.isWait() is True:
            if self.enableTrade is True:
                self.ctaTemplate.buy(tick.upperLimit, int32(self.maxPosition))
            self.writeCtaLog('开多' + str(self.maxPosition) + '手')
            self.duo_position = self.maxPosition
            self.kong_position = 0
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)

        if preStatus == 'lockingshort' and status == 'holdingshort' and self.isWait() is True:
            if self.enableTrade is True:
                self.ctaTemplate.short(tick.upperLimit, int32(self.maxPosition))
            self.writeCtaLog('开空' + str(self.maxPosition / 2) + '手')
            self.duo_position = 0
            self.kong_position = self.maxPosition
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)

    def trade(self, tick):
        self.buy(tick)
        self.short(tick)
        self.closePosition(tick)
        #self.lock(tick)
        #self.unlock(tick)

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

    def writeCtaLog(self, content):
        if self.ctaTemplate is None:
            print content
        else:
            self.ctaTemplate.writeCtaLog(u'' + content)
            print content



