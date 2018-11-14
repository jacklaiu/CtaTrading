# encoding: UTF-8
import pymysql.cursors
from numpy import int32

host='212.64.7.83'
user='jacklaiu'
password='queue11235813'
db='trading'
charset='utf8mb4'
cursorclass=pymysql.cursors.DictCursor


# host='localhost'
# user='root'
# password='123456'
# db='conceptlistener'
# charset='utf8mb4'
# cursorclass=pymysql.cursors.DictCursor

def getConn():
    connection = pymysql.connect(host=host,
                                 user=user,
                                 password=password,
                                 db=db,
                                 charset=charset,
                                 cursorclass=cursorclass)
    return connection

def updatemany(sql, arr_values):
    connection = getConn()
    try:
        with connection.cursor() as cursor:
            cursor.executemany(sql, arr_values)
        connection.commit()
    except Exception as e:
        connection.rollback()
    finally:
        connection.close()

def update(sql, values):
    connection = getConn()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, values)
        connection.commit()
    except Exception as e:
        connection.rollback()
    finally:
        connection.close()

def select(sql, values):
    connection = getConn()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, values)
            result = cursor.fetchall()
            return result
    finally:
        connection.close()

def updatePosition(security, duo_position, kong_position):
    if security.find('.') != -1:
        security = security[0:security.find('.')].lower()
    count = select("select count(*) as count from t_position where security=%s", (security))[0]['count']
    if count == 0:
        update('insert into t_position(duo_position, kong_position, security) values(%s,%s,%s)', (str(duo_position), str(kong_position), security))
    else:
        update('update t_position set duo_position=%s, kong_position=%s where security=%s', (str(duo_position), str(kong_position), security))

# 如果要重新开始，就在数据库把这个值置0
def readDuoPosition(security):
    if security.find('.') != -1:
        security = security[0:security.find('.')].lower()
    if select("select count(*) as count from t_position where security=%s", (security))[0]['count'] == 0:
        print u'数据库中找不到security对应的记录'
        exit()
    if security is None:
        return
    return int32(select('select duo_position from t_position where security=%s', (security))[0]['duo_position'])

# 如果要重新开始，就在数据库把这个值置0
def readKongPosition(security):
    if security.find('.') != -1:
        security = security[0:security.find('.')].lower()
    if select("select count(*) as count from t_position where security=%s", (security))[0]['count'] == 0:
        print u'数据库中找不到security对应的记录'
        exit()
    if security is None:
        return
    return int32(select('select kong_position from t_position where security=%s', (security))[0]['kong_position'])

# 这个值只会在数据库改
def readMaxPosition(security):
    if security.find('.') != -1:
        security = security[0:security.find('.')].lower()
    if select("select count(*) as count from t_position where security=%s", (security))[0]['count'] == 0:
        print u'数据库中找不到security对应的记录'
        exit()
    if security is None:
        return
    return int32(select('select max_position from t_position where security=%s', (security))[0]['max_position'])
