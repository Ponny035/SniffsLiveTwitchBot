import os

from mysql.connector import connect, Error


class DBManager:
    def __init__(self):

        self.environment = os.environ.get("env", "")
        self.table = "User_Info"
        self.connect_db = None
        self.cursor = None

        try:
            if(self.environment == "dev"):
                print("Connect db on DEVELOPMENT environment")
                # with open("./data/dev_db", "r", encoding="utf-8") as f:
                #     HOST, USERNAME, PASSWORD, DATABASE = (l.strip() for l in f.readlines())
            elif(self.environment == "prod"):
                print("Connect db on PRODUCTION environment")
                # with open("./data/db", "r", encoding="utf-8") as f:
                #     HOST, USERNAME, PASSWORD, DATABASE = (l.strip() for l in f.readlines())
            self.connect_db = connect(
                host=os.environ.get("DB_HOST", ""),
                username=os.environ.get("DB_USER", ""),
                password=os.environ.get("DB_PASS", ""),
                database=os.environ.get("DB_NAME", "")
            )
            self.cursor = self.connect_db.cursor()
        except Error as e:
            print(e)

    def check_connection(self):
        if not (self.connect_db.is_connected()):
            self.connect_db = connect(
                host=os.environ.get("DB_HOST", ""),
                username=os.environ.get("DB_USER", ""),
                password=os.environ.get("DB_PASS", ""),
                database=os.environ.get("DB_NAME", "")
            )

    def sql_do(self, sql):
        self.check_connection()
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Error as e:
            print(e)

    def check_exist(self, username):
        self.check_connection()
        sql_statement = 'SELECT 1 FROM {} WHERE User_Name = (%s)'.format(self.table)
        try:
            self.cursor.execute(sql_statement, (username,))
            if self.cursor.fetchone():
                return True
            else:
                return False
        except Error as e:
            print(e)
            return False

    def insert(self, userdata):
        self.check_connection()
        sql_statement = ('INSERT INTO {} (User_Name, Coin, Watch_Time, Sub_Month, Update_By) VALUES (%(username)s, %(coin)s, %(watchtime)s, %(submonth)s, 1)'.format(self.table))
        try:
            self.cursor.execute(sql_statement, userdata)
            self.connect_db.commit()
            return "success"
        except Error as e:
            print(e)

    def retrieve(self, username):
        self.check_connection()
        sql_statement = 'SELECT * FROM {} WHERE User_Name = (%s)'.format(self.table)
        try:
            self.cursor.execute(sql_statement, (username,))
            record = self.cursor.fetchone()
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
            return None

    def update(self, userdata):
        self.check_connection()
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
        sql_statement = 'UPDATE {} SET'.format(self.table)
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
            self.cursor.execute(sql_statement, value)
            self.connect_db.commit()
            return "success"
        except Error as e:
            print(e)

    def delete(self, username):
        self.check_connection()
        sql_statement = ('DELETE FROM {} WHERE User_Name = (%s)'.format(self.table))
        try:
            self.cursor.execute(sql_statement, (username,))
            self.connect_db.commit()
            return "success"
        except Error as e:
            print(e)
