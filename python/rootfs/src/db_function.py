import os

from mysql.connector import connect, Error


environment = os.environ.get("env", "")
table = "User_Info"


def db_connect():
    try:
        conn = connect(
            host=os.environ.get("DB_HOST", ""),
            username=os.environ.get("DB_USER", ""),
            password=os.environ.get("DB_PASS", ""),
            database=os.environ.get("DB_NAME", "")
        )
    except Error as e:
        print(e)
    return conn


def sql_do(sql):
    try:
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchall()
    except Error as e:
        print(e)
        conn.close()


def check_exist(username):
    sql_statement = 'SELECT 1 FROM {} WHERE User_Name = (%s)'.format(table)
    try:
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(sql_statement, (username,))
        if cur.fetchone():
            return True
        else:
            return False
    except Error as e:
        print(e)
        conn.close()
        return False


def insert(userdata):
    sql_statement = ('INSERT INTO {} (User_Name, Coin, Watch_Time, Sub_Month, Update_By) VALUES (%(username)s, %(coin)s, %(watchtime)s, %(submonth)s, 1)'.format(table))
    try:
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(sql_statement, userdata)
        conn.commit()
        return "success"
    except Error as e:
        print(e)
        conn.close()


def retrieve(username):
    sql_statement = 'SELECT * FROM {} WHERE User_Name = (%s)'.format(table)
    try:
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(sql_statement, (username,))
        record = cur.fetchone()
        if record:
            userdata = {
                "username": record[0],
                "coin": record[1],
                "watchtime": record[2],
                "submonth": record[3]
            }
            return userdata
        else:
            return None
    except Error as e:
        print(e)
        conn.close()
        return None


def update(userdata):
    try:
        username = userdata["username"]
    except KeyError:
        return "failed"
    try:
        coin = userdata["coin"]
    except KeyError:
        coin = None
    try:
        watchtime = userdata["watchtime"]
    except KeyError:
        watchtime = None
    try:
        submonth = userdata["submonth"]
    except KeyError:
        submonth = None
    sql_statement = 'UPDATE {} SET'.format(table)
    value = ()
    if coin is not None:
        sql_statement += " Coin = %s"
        value += (coin,)
    if watchtime is not None:
        sql_statement += " ,Watch_Time = %s"
        value += (watchtime,)
    if submonth is not None:
        sql_statement += " ,Sub_Month = %s"
        value += (submonth,)
    sql_statement += " WHERE User_Name = %s"
    value += (username,)
    try:
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(sql_statement, value)
        conn.commit()
        return "success"
    except Error as e:
        print(e)
        conn.close()


def delete(username):
    sql_statement = ('DELETE FROM {} WHERE User_Name = (%s)'.format(table))
    try:
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(sql_statement, (username,))
        conn.commit()
        return "success"
    except Error as e:
        print(e)
        conn.close()
