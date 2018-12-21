#: encoding: utf8

import requests
import base.Util as util
import base.Dao as dao

enable = False

def sendEmail(subject, content, receivers='jacklaiu@qq.com'):
    print("@@@@@@@@@@@@@->subject: " + subject + " content: " + content)
    if enable is False:
        return
    url = 'http://mail.jacklaiu.cn:64210/smtpclient/sendHtml?subject='+subject+'&content='+subject+'&receivers='+receivers
    requests.get(url)

def notifyVolumeUnusual(security):
    currentTimeString = util.getYMDHMS()
    a = '<a href="http://212.64.7.83:5288/">查看行情</a>'
    sendEmail(subject='瞬间成交量大增_' + security, content='' + a)

def notifyTrade(security):
    currentTimeString = util.getYMDHMS()
    duo = str(int(dao.readDuoPosition(security=security)))
    kon = str(int(dao.readKongPosition(security=security)))
    max = str(int(dao.readMaxPosition(security=security)))
    a = '<p>duo: <strong>'+duo+'</strong></p><p>kon: <strong>'+kon+'</strong></p><p>max: <strong>'+max+'</strong></p>'
    sendEmail(subject='触发交易动作_' + security, content='' + a)

def notifyOpenKon(security, currentTimeString=None):
    if currentTimeString is None:
        currentTimeString = util.getYMDHMS()
    a = '<a href="http://212.64.7.83:5288/">查看行情</a>'
    sendEmail(subject='Kon开_' + security, content='' + a)

def notifyOpenDuo(security, currentTimeString=None):
    if currentTimeString is None:
        currentTimeString = util.getYMDHMS()
    a = '<a href="http://212.64.7.83:5288/">查看行情</a>'
    sendEmail(subject='Duo开_' + security, content='' + a)

def notifyCloseKon(security, currentTimeString=None):
    if currentTimeString is None:
        currentTimeString = util.getYMDHMS()
    a = '<a href="http://212.64.7.83:5288/">查看行情</a>'
    sendEmail(subject='Kon平_' + security, content='' + a)

def notifyCloseDuo(security, currentTimeString=None):
    if currentTimeString is None:
        currentTimeString = util.getYMDHMS()
    a = '<a href="http://212.64.7.83:5288/">查看行情</a>'
    sendEmail(subject='Duo平_' + security, content='' + a)