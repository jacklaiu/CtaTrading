# encoding: UTF-8
import pymysql.cursors

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

def updateDuoPosition(posi):
    update('update t_position set duo_position=%s', (posi))

def updateKongPosition(posi):
    update('update t_position set kong_position=%s', (posi))

def readDuoPosition():
    return select('select duo_position from t_position', ())

ret = readDuoPosition()
print