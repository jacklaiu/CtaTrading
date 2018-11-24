# encoding: UTF-8
import tushare as ts
import time
import datetime
import jqdatasdk

def getTimeSerial(starttime, count, periodSec):
    ts = string2timestamp(starttime)
    list = []
    while count > 0:
        ts = ts + periodSec
        list.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)))
        count = count - 1
    return list

def getYMDHMS():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def getYMD():
    return time.strftime("%Y-%m-%d", time.localtime())

def getHMS():
    return time.strftime("%H:%M:%S", time.localtime())

def getTimeStamp():
    millis = int(round(time.time() * 1000))
    return millis

def string2timestamp(strValue):
    try:
        d = datetime.datetime.strptime(strValue, "%Y-%m-%d %H:%M:%S.%f")
        t = d.timetuple()
        timeStamp = int(time.mktime(t))
        timeStamp = float(str(timeStamp) + str("%06d" % d.microsecond)) / 1000000
        return timeStamp
    except ValueError as e:
        d = datetime.datetime.strptime(strValue, "%Y-%m-%d %H:%M:%S")
        t = d.timetuple()
        timeStamp = int(time.mktime(t))
        timeStamp = float(str(timeStamp) + str("%06d" % d.microsecond)) / 1000000
        return timeStamp

def getFormatToday():
    return time.strftime("%Y-%m-%d", time.localtime())

def getPreDayYMD(num=1, startdate=None):
    today=datetime.date.today()
    if startdate is not None:
        arr = startdate.split("-")
        today = datetime.date(int(arr[0]), int(arr[1]), int(arr[2]))
    oneday=datetime.timedelta(days=num)
    d=today-oneday
    return str(d)

def get_concept_securities():
    df = ts.get_concept_classified()
    values = df.values
    concept_code_dict = {}
    for row in values:
        code = row[0]
        c_name = row[2]
        if c_name not in concept_code_dict:
            concept_code_dict.setdefault(c_name, [code])
        else:
            concept_code_dict[c_name].append(code)
    return concept_code_dict


def initOpenDateTempFile():
    OpenList = ts.trade_cal()
    rows = OpenList[OpenList.isOpen == 1].values[-888:]
    f = open("../temp_OpenDate.txt", "w")
    f.write("")
    f.close()
    f = open("temp_OpenDate.txt", "a")
    for row in rows:
        date = row[0]
        f.write(date + ";")
    f.close()

def getOpenDates():
    #f = open(os.path.dirname(__file__) + "/temp_OpenDate.txt", "r")
    #str = f.read()
    str = "2015-05-18;2015-05-19;2015-05-20;2015-05-21;2015-05-22;2015-05-25;2015-05-26;2015-05-27;2015-05-28;2015-05-29;2015-06-01;2015-06-02;2015-06-03;2015-06-04;2015-06-05;2015-06-08;2015-06-09;2015-06-10;2015-06-11;2015-06-12;2015-06-15;2015-06-16;2015-06-17;2015-06-18;2015-06-19;2015-06-23;2015-06-24;2015-06-25;2015-06-26;2015-06-29;2015-06-30;2015-07-01;2015-07-02;2015-07-03;2015-07-06;2015-07-07;2015-07-08;2015-07-09;2015-07-10;2015-07-13;2015-07-14;2015-07-15;2015-07-16;2015-07-17;2015-07-20;2015-07-21;2015-07-22;2015-07-23;2015-07-24;2015-07-27;2015-07-28;2015-07-29;2015-07-30;2015-07-31;2015-08-03;2015-08-04;2015-08-05;2015-08-06;2015-08-07;2015-08-10;2015-08-11;2015-08-12;2015-08-13;2015-08-14;2015-08-17;2015-08-18;2015-08-19;2015-08-20;2015-08-21;2015-08-24;2015-08-25;2015-08-26;2015-08-27;2015-08-28;2015-08-31;2015-09-01;2015-09-02;2015-09-07;2015-09-08;2015-09-09;2015-09-10;2015-09-11;2015-09-14;2015-09-15;2015-09-16;2015-09-17;2015-09-18;2015-09-21;2015-09-22;2015-09-23;2015-09-24;2015-09-25;2015-09-28;2015-09-29;2015-09-30;2015-10-08;2015-10-09;2015-10-12;2015-10-13;2015-10-14;2015-10-15;2015-10-16;2015-10-19;2015-10-20;2015-10-21;2015-10-22;2015-10-23;2015-10-26;2015-10-27;2015-10-28;2015-10-29;2015-10-30;2015-11-02;2015-11-03;2015-11-04;2015-11-05;2015-11-06;2015-11-09;2015-11-10;2015-11-11;2015-11-12;2015-11-13;2015-11-16;2015-11-17;2015-11-18;2015-11-19;2015-11-20;2015-11-23;2015-11-24;2015-11-25;2015-11-26;2015-11-27;2015-11-30;2015-12-01;2015-12-02;2015-12-03;2015-12-04;2015-12-07;2015-12-08;2015-12-09;2015-12-10;2015-12-11;2015-12-14;2015-12-15;2015-12-16;2015-12-17;2015-12-18;2015-12-21;2015-12-22;2015-12-23;2015-12-24;2015-12-25;2015-12-28;2015-12-29;2015-12-30;2015-12-31;2016-01-04;2016-01-05;2016-01-06;2016-01-07;2016-01-08;2016-01-11;2016-01-12;2016-01-13;2016-01-14;2016-01-15;2016-01-18;2016-01-19;2016-01-20;2016-01-21;2016-01-22;2016-01-25;2016-01-26;2016-01-27;2016-01-28;2016-01-29;2016-02-01;2016-02-02;2016-02-03;2016-02-04;2016-02-05;2016-02-15;2016-02-16;2016-02-17;2016-02-18;2016-02-19;2016-02-22;2016-02-23;2016-02-24;2016-02-25;2016-02-26;2016-02-29;2016-03-01;2016-03-02;2016-03-03;2016-03-04;2016-03-07;2016-03-08;2016-03-09;2016-03-10;2016-03-11;2016-03-14;2016-03-15;2016-03-16;2016-03-17;2016-03-18;2016-03-21;2016-03-22;2016-03-23;2016-03-24;2016-03-25;2016-03-28;2016-03-29;2016-03-30;2016-03-31;2016-04-01;2016-04-05;2016-04-06;2016-04-07;2016-04-08;2016-04-11;2016-04-12;2016-04-13;2016-04-14;2016-04-15;2016-04-18;2016-04-19;2016-04-20;2016-04-21;2016-04-22;2016-04-25;2016-04-26;2016-04-27;2016-04-28;2016-04-29;2016-05-03;2016-05-04;2016-05-05;2016-05-06;2016-05-09;2016-05-10;2016-05-11;2016-05-12;2016-05-13;2016-05-16;2016-05-17;2016-05-18;2016-05-19;2016-05-20;2016-05-23;2016-05-24;2016-05-25;2016-05-26;2016-05-27;2016-05-30;2016-05-31;2016-06-01;2016-06-02;2016-06-03;2016-06-06;2016-06-07;2016-06-08;2016-06-13;2016-06-14;2016-06-15;2016-06-16;2016-06-17;2016-06-20;2016-06-21;2016-06-22;2016-06-23;2016-06-24;2016-06-27;2016-06-28;2016-06-29;2016-06-30;2016-07-01;2016-07-04;2016-07-05;2016-07-06;2016-07-07;2016-07-08;2016-07-11;2016-07-12;2016-07-13;2016-07-14;2016-07-15;2016-07-18;2016-07-19;2016-07-20;2016-07-21;2016-07-22;2016-07-25;2016-07-26;2016-07-27;2016-07-28;2016-07-29;2016-08-01;2016-08-02;2016-08-03;2016-08-04;2016-08-05;2016-08-08;2016-08-09;2016-08-10;2016-08-11;2016-08-12;2016-08-15;2016-08-16;2016-08-17;2016-08-18;2016-08-19;2016-08-22;2016-08-23;2016-08-24;2016-08-25;2016-08-26;2016-08-29;2016-08-30;2016-08-31;2016-09-01;2016-09-02;2016-09-05;2016-09-06;2016-09-07;2016-09-08;2016-09-09;2016-09-12;2016-09-13;2016-09-14;2016-09-19;2016-09-20;2016-09-21;2016-09-22;2016-09-23;2016-09-26;2016-09-27;2016-09-28;2016-09-29;2016-09-30;2016-10-10;2016-10-11;2016-10-12;2016-10-13;2016-10-14;2016-10-17;2016-10-18;2016-10-19;2016-10-20;2016-10-21;2016-10-24;2016-10-25;2016-10-26;2016-10-27;2016-10-28;2016-10-31;2016-11-01;2016-11-02;2016-11-03;2016-11-04;2016-11-07;2016-11-08;2016-11-09;2016-11-10;2016-11-11;2016-11-14;2016-11-15;2016-11-16;2016-11-17;2016-11-18;2016-11-21;2016-11-22;2016-11-23;2016-11-24;2016-11-25;2016-11-28;2016-11-29;2016-11-30;2016-12-01;2016-12-02;2016-12-05;2016-12-06;2016-12-07;2016-12-08;2016-12-09;2016-12-12;2016-12-13;2016-12-14;2016-12-15;2016-12-16;2016-12-19;2016-12-20;2016-12-21;2016-12-22;2016-12-23;2016-12-26;2016-12-27;2016-12-28;2016-12-29;2016-12-30;2017-01-03;2017-01-04;2017-01-05;2017-01-06;2017-01-09;2017-01-10;2017-01-11;2017-01-12;2017-01-13;2017-01-16;2017-01-17;2017-01-18;2017-01-19;2017-01-20;2017-01-23;2017-01-24;2017-01-25;2017-01-26;2017-02-03;2017-02-06;2017-02-07;2017-02-08;2017-02-09;2017-02-10;2017-02-13;2017-02-14;2017-02-15;2017-02-16;2017-02-17;2017-02-20;2017-02-21;2017-02-22;2017-02-23;2017-02-24;2017-02-27;2017-02-28;2017-03-01;2017-03-02;2017-03-03;2017-03-06;2017-03-07;2017-03-08;2017-03-09;2017-03-10;2017-03-13;2017-03-14;2017-03-15;2017-03-16;2017-03-17;2017-03-20;2017-03-21;2017-03-22;2017-03-23;2017-03-24;2017-03-27;2017-03-28;2017-03-29;2017-03-30;2017-03-31;2017-04-05;2017-04-06;2017-04-07;2017-04-10;2017-04-11;2017-04-12;2017-04-13;2017-04-14;2017-04-17;2017-04-18;2017-04-19;2017-04-20;2017-04-21;2017-04-24;2017-04-25;2017-04-26;2017-04-27;2017-04-28;2017-05-02;2017-05-03;2017-05-04;2017-05-05;2017-05-08;2017-05-09;2017-05-10;2017-05-11;2017-05-12;2017-05-15;2017-05-16;2017-05-17;2017-05-18;2017-05-19;2017-05-22;2017-05-23;2017-05-24;2017-05-25;2017-05-26;2017-05-31;2017-06-01;2017-06-02;2017-06-05;2017-06-06;2017-06-07;2017-06-08;2017-06-09;2017-06-12;2017-06-13;2017-06-14;2017-06-15;2017-06-16;2017-06-19;2017-06-20;2017-06-21;2017-06-22;2017-06-23;2017-06-26;2017-06-27;2017-06-28;2017-06-29;2017-06-30;2017-07-03;2017-07-04;2017-07-05;2017-07-06;2017-07-07;2017-07-10;2017-07-11;2017-07-12;2017-07-13;2017-07-14;2017-07-17;2017-07-18;2017-07-19;2017-07-20;2017-07-21;2017-07-24;2017-07-25;2017-07-26;2017-07-27;2017-07-28;2017-07-31;2017-08-01;2017-08-02;2017-08-03;2017-08-04;2017-08-07;2017-08-08;2017-08-09;2017-08-10;2017-08-11;2017-08-14;2017-08-15;2017-08-16;2017-08-17;2017-08-18;2017-08-21;2017-08-22;2017-08-23;2017-08-24;2017-08-25;2017-08-28;2017-08-29;2017-08-30;2017-08-31;2017-09-01;2017-09-04;2017-09-05;2017-09-06;2017-09-07;2017-09-08;2017-09-11;2017-09-12;2017-09-13;2017-09-14;2017-09-15;2017-09-18;2017-09-19;2017-09-20;2017-09-21;2017-09-22;2017-09-25;2017-09-26;2017-09-27;2017-09-28;2017-09-29;2017-10-09;2017-10-10;2017-10-11;2017-10-12;2017-10-13;2017-10-16;2017-10-17;2017-10-18;2017-10-19;2017-10-20;2017-10-23;2017-10-24;2017-10-25;2017-10-26;2017-10-27;2017-10-30;2017-10-31;2017-11-01;2017-11-02;2017-11-03;2017-11-06;2017-11-07;2017-11-08;2017-11-09;2017-11-10;2017-11-13;2017-11-14;2017-11-15;2017-11-16;2017-11-17;2017-11-20;2017-11-21;2017-11-22;2017-11-23;2017-11-24;2017-11-27;2017-11-28;2017-11-29;2017-11-30;2017-12-01;2017-12-04;2017-12-05;2017-12-06;2017-12-07;2017-12-08;2017-12-11;2017-12-12;2017-12-13;2017-12-14;2017-12-15;2017-12-18;2017-12-19;2017-12-20;2017-12-21;2017-12-22;2017-12-25;2017-12-26;2017-12-27;2017-12-28;2017-12-29;2018-01-02;2018-01-03;2018-01-04;2018-01-05;2018-01-08;2018-01-09;2018-01-10;2018-01-11;2018-01-12;2018-01-15;2018-01-16;2018-01-17;2018-01-18;2018-01-19;2018-01-22;2018-01-23;2018-01-24;2018-01-25;2018-01-26;2018-01-29;2018-01-30;2018-01-31;2018-02-01;2018-02-02;2018-02-05;2018-02-06;2018-02-07;2018-02-08;2018-02-09;2018-02-12;2018-02-13;2018-02-14;2018-02-22;2018-02-23;2018-02-26;2018-02-27;2018-02-28;2018-03-01;2018-03-02;2018-03-05;2018-03-06;2018-03-07;2018-03-08;2018-03-09;2018-03-12;2018-03-13;2018-03-14;2018-03-15;2018-03-16;2018-03-19;2018-03-20;2018-03-21;2018-03-22;2018-03-23;2018-03-26;2018-03-27;2018-03-28;2018-03-29;2018-03-30;2018-04-02;2018-04-03;2018-04-04;2018-04-09;2018-04-10;2018-04-11;2018-04-12;2018-04-13;2018-04-16;2018-04-17;2018-04-18;2018-04-19;2018-04-20;2018-04-23;2018-04-24;2018-04-25;2018-04-26;2018-04-27;2018-05-02;2018-05-03;2018-05-04;2018-05-07;2018-05-08;2018-05-09;2018-05-10;2018-05-11;2018-05-14;2018-05-15;2018-05-16;2018-05-17;2018-05-18;2018-05-21;2018-05-22;2018-05-23;2018-05-24;2018-05-25;2018-05-28;2018-05-29;2018-05-30;2018-05-31;2018-06-01;2018-06-04;2018-06-05;2018-06-06;2018-06-07;2018-06-08;2018-06-11;2018-06-12;2018-06-13;2018-06-14;2018-06-15;2018-06-19;2018-06-20;2018-06-21;2018-06-22;2018-06-25;2018-06-26;2018-06-27;2018-06-28;2018-06-29;2018-07-02;2018-07-03;2018-07-04;2018-07-05;2018-07-06;2018-07-09;2018-07-10;2018-07-11;2018-07-12;2018-07-13;2018-07-16;2018-07-17;2018-07-18;2018-07-19;2018-07-20;2018-07-23;2018-07-24;2018-07-25;2018-07-26;2018-07-27;2018-07-30;2018-07-31;2018-08-01;2018-08-02;2018-08-03;2018-08-06;2018-08-07;2018-08-08;2018-08-09;2018-08-10;2018-08-13;2018-08-14;2018-08-15;2018-08-16;2018-08-17;2018-08-20;2018-08-21;2018-08-22;2018-08-23;2018-08-24;2018-08-27;2018-08-28;2018-08-29;2018-08-30;2018-08-31;2018-09-03;2018-09-04;2018-09-05;2018-09-06;2018-09-07;2018-09-10;2018-09-11;2018-09-12;2018-09-13;2018-09-14;2018-09-17;2018-09-18;2018-09-19;2018-09-20;2018-09-21;2018-09-25;2018-09-26;2018-09-27;2018-09-28;2018-10-08;2018-10-09;2018-10-10;2018-10-11;2018-10-12;2018-10-15;2018-10-16;2018-10-17;2018-10-18;2018-10-19;2018-10-22;2018-10-23;2018-10-24;2018-10-25;2018-10-26;2018-10-29;2018-10-30;2018-10-31;2018-11-01;2018-11-02;2018-11-05;2018-11-06;2018-11-07;2018-11-08;2018-11-09;2018-11-12;2018-11-13;2018-11-14;2018-11-15;2018-11-16;2018-11-19;2018-11-20;2018-11-21;2018-11-22;2018-11-23;2018-11-26;2018-11-27;2018-11-28;2018-11-29;2018-11-30;2018-12-03;2018-12-04;2018-12-05;2018-12-06;2018-12-07;2018-12-10;2018-12-11;2018-12-12;2018-12-13;2018-12-14;2018-12-17;2018-12-18;2018-12-19;2018-12-20;2018-12-21;2018-12-24;2018-12-25;2018-12-26;2018-12-27;2018-12-28;2018-12-31;"
    if str != "":
        dates = str.split(";")
    else: return None
    return dates

def get_k_data(df, start, end):
    ret = df[(df['date'] >= start) & (df['date'] <= end)]
    return ret

def isOpen(date):
    OpenDates = getOpenDates()
    str = ";".join(OpenDates)
    return date in str

def preOpenDate(date, leftCount=1):
    OpenDates = getOpenDates()
    index = 0
    for d in OpenDates:
        if d == date:
            return OpenDates[index - int(leftCount)]
        index = index + 1
    return None

def getLastestOpenDate(date=getYMD()):
    hms = getHMS()
    if hms >= '15:00:00' and isOpen(date):
        return date
    if hms < '15:00:00' and isOpen(date):
        return preOpenDate(date, 1)
    count = 0
    while True:
        count = count + 1
        if isOpen(date) == False:
            date = getPreDayYMD(1, date)
            continue
        else:
            break
    return date

def nextOpenDate(date, rightCount=1):
    OpenDates = getOpenDates()
    index = 0
    for d in OpenDates:
        if d == date:
            if index + rightCount < OpenDates.__len__() -1:
                return OpenDates[index + rightCount]
            else:
                break
        index = index + 1
    return None

def isOpenFromJqdata(jqDataAccount='13268108673', jqDataPassword='king20110713'):
    jqdatasdk.auth(jqDataAccount, jqDataPassword)
    array = jqdatasdk.get_trade_days(start_date='2018-11-01', end_date='2019-12-31')
    today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    for date in array:
        datestr = str(date)
        if today == datestr:
            return True
    return False
