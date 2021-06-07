from mysql.connector import connect, Error


class DBManager(connect,):
    def __init__(self,environment):

        self.environment = environment

        try:
            if(environment == "dev"):
                print("Connect db on DEVELOPMENT environment")
                with open("./data/dev_db", "r", encoding="utf-8") as f:
                    HOST, USERNAME, PASSWORD = (l.strip() for l in f.readlines())
                with super().__init__(
                    host=HOST,
                    user=USERNAME,
                    password=PASSWORD,
                ) as connection:
                    print(connection)
        except Error as e:
            print(e)
