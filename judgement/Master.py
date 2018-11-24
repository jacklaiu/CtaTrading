
class Judgement_Basic():
    def __init__(self, base):
        self.base = base

    def judgeOpenBuy(self):
        return self.base.now_pricePosi == self.base.pricePosi_top

    def judgeOpenShort(self):
        return self.base.now_pricePosi == self.base.pricePosi_bottom

    def judgeCloseBuy(self):
        return self.base.now_pricePosi > self.base.pricePosi_top

    def judgeCloseShort(self):
        return self.base.now_pricePosi < self.base.pricePosi_bottom

class Judgement_Power():
    def __init__(self, base):
        self.base = base

    def judgeOpenBuy(self):
        return True

    def judgeOpenShort(self):
        return True

    def judgeCloseBuy(self):
        return True

    def judgeCloseShort(self):
        return True

    def getLifeEMAK(self, preCount=0):
        f = self.getEMAK(ematype='5', preCount=preCount)
        t = self.getEMAK(ematype='10', preCount=preCount)
        return f + t

    def getEMADistance(self, ematypes=('5', '10', '20', '40', '60'), preCount=0):
        values = []
        for ematype in ematypes:
            values.append(float(self.base.df.loc[self.base.indexList[-1 - preCount], 'EMA' + ematype]))
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

    def getEMAK(self, preCount=0, ematype='5'):
        ema_1 = float(self.base.df.loc[self.base.indexList[-1 - preCount], 'EMA' + ematype])
        a = ema_1 / 1000
        ema_2 = float(self.base.df.loc[self.base.indexList[-2 - preCount], 'EMA' + ematype])
        return (ema_1 - ema_2) / a * 3

class Judgement_K():
    def __init__(self, base):
        self.base = base

    def judgeOpenBuy(self):
        return True

    def judgeOpenShort(self):
        return True

    def judgeCloseBuy(self):
        return True

    def judgeCloseShort(self):
        return True

    def getLifeEMAK(self, preCount=0):
        f = self.getEMAK(ematype='5', preCount=preCount)
        t = self.getEMAK(ematype='10', preCount=preCount)
        return f + t

    def getEMADistance(self, ematypes=('5', '10', '20', '40', '60'), preCount=0):
        values = []
        for ematype in ematypes:
            values.append(float(self.base.df.loc[self.base.indexList[-1 - preCount], 'EMA' + ematype]))
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

    def getEMAK(self, preCount=0, ematype='5'):
        ema_1 = float(self.base.df.loc[self.base.indexList[-1 - preCount], 'EMA' + ematype])
        a = ema_1 / 1000
        ema_2 = float(self.base.df.loc[self.base.indexList[-2 - preCount], 'EMA' + ematype])
        return (ema_1 - ema_2) / a * 3

class Judgement_Master():

    def __init__(self, base):
        self.base = base
        self.j_basic = Judgement_Basic(base)
        self.j_power = Judgement_Power(base)
        self.j_k = Judgement_K(base)

    def judgeOpenBuy(self):
        return (
                self.j_basic.judgeOpenBuy()
                and self.j_power.judgeOpenBuy()
                and self.j_k.judgeOpenBuy()
        )

    def judgeOpenShort(self):
        return (
                self.j_basic.judgeOpenShort()
                and self.j_power.judgeOpenShort()
                and self.j_k.judgeOpenBuy()
        )

    def judgeCloseBuy(self):
        return (
                self.j_basic.judgeCloseBuy()
                and self.j_power.judgeCloseBuy()
                and self.j_k.judgeOpenBuy()
        )

    def judgeCloseShort(self):
        return (
                self.j_basic.judgeCloseShort()
                and self.j_power.judgeCloseShort()
                and self.j_k.judgeOpenBuy()
        )

