
class Judgement_Basic():
    def __init__(self, base):
        self.base = base

    def judgeOpenBuy(self, indexCount):
        return self.base.now_pricePosi == self.base.pricePosi_top

    def judgeOpenShort(self, indexCount):
        return self.base.now_pricePosi == self.base.pricePosi_bottom

    def judgeCloseBuy(self, indexCount):
        return False#self.base.now_pricePosi > self.base.pricePosi_top

    def judgeCloseShort(self, indexCount):
        return False#self.base.now_pricePosi < self.base.pricePosi_bottom

class Judgement_Power():
    def __init__(self, base):
        self.base = base

    def judgeOpenBuy(self, indexCount):
        if self.base.lastestAbsK is None:
            return True
        else :
            return self.getLifeAbsEMAK(indexCount) > self.base.lastestAbsK

    def judgeOpenShort(self, indexCount):
        if self.base.lastestAbsK is None:
            return True
        else :
            return self.getLifeAbsEMAK(indexCount) > self.base.lastestAbsK

    def judgeCloseBuy(self, indexCount):
        return False

    def judgeCloseShort(self, indexCount):
        return False

    def getEMAK(self, indexCount=0, ematype='5'):
        ema_now = float(self.base.df.loc[self.base.indexList[indexCount], 'EMA' + ematype])
        if indexCount == 0:
            ema_pre = ema_now
        else:
            ema_pre = float(self.base.df.loc[self.base.indexList[indexCount - 1], 'EMA' + ematype])
        banlance = ema_now / 1000
        return (ema_now - ema_pre) / banlance * 3

    def getLifeAbsEMAK(self, indexCount):
        f = self.getEMAK(ematype='5', indexCount=indexCount)
        t = self.getEMAK(ematype='10', indexCount=indexCount)
        return abs(f + t)

class Judgement_K():
    def __init__(self, base):
        self.base = base

    def judgeOpenBuy(self, indexCount):
        return self.getMAK(indexCount, matype='120') > 1

    def judgeOpenShort(self, indexCount):
        return self.getMAK(indexCount, matype='120') < -1

    def judgeCloseBuy(self, indexCount):
        return False

    def judgeCloseShort(self, indexCount):
        return False

    def getMAK(self, indexCount=0, matype='5'):
        ma_now = float(self.base.df.loc[self.base.indexList[indexCount], 'MA' + matype])
        if indexCount == 0:
            ma_pre = ma_now
        else:
            ma_pre = float(self.base.df.loc[self.base.indexList[indexCount - 1], 'MA' + matype])
        banlance = ma_now / 1000
        return (ma_now - ma_pre) / banlance * 3

class Judgement_Master():

    def __init__(self, base):
        self.base = base
        self.j_basic = Judgement_Basic(base)
        self.j_power = Judgement_Power(base)
        self.j_k = Judgement_K(base)

    def judgeOpenBuy(self, indexCount):
        return (
                (
                    True
                    and self.j_basic.judgeOpenBuy(indexCount)
                )
        )

    def judgeOpenShort(self, indexCount):
        return (
                (
                    True
                    and self.j_basic.judgeOpenShort(indexCount)
                )

        )

    def judgeCloseBuy(self, indexCount):
        return (
                (
                    False
                    or self.j_basic.judgeCloseBuy(indexCount)
                )
        )

    def judgeCloseShort(self, indexCount):
        return (
                (
                    False
                    or self.j_basic.judgeCloseShort(indexCount)
                )
        )


















# def getLifeEMAK(self, preCount=0):
#     f = self.getEMAK(ematype='5', preCount=preCount)
#     t = self.getEMAK(ematype='10', preCount=preCount)
#     return f + t
#
# def getEMADistance(self, ematypes=('5', '10', '20', '40', '60'), preCount=0):
#     values = []
#     for ematype in ematypes:
#         values.append(float(self.base.df.loc[self.base.indexList[-1 - preCount], 'EMA' + ematype]))
#     preV = None
#     firstV = None
#     distance = 0
#     for value in values:
#         if firstV is None:
#             firstV = value
#         if preV is not None:
#             distance = distance + abs(value - preV) / ematypes.__len__()
#         preV = value
#     return round(distance / ematypes.__len__() / firstV, 8) * 100
#
