from bot import TwitchBot
from db_connect import DBManager
import sys

def main(environment):
    bot = TwitchBot(environment)
    db = DBManager(environment)
    bot.run()
    db.run()

if __name__ == "__main__":
    environment = sys.argv[1]
    try:
        if((environment == "dev") or (environment == "prod")):
            main(environment)
        else:
            raise TypeError("Only 2 types are allow (dev/production)")

    except Exception as msg:
        print(msg)
