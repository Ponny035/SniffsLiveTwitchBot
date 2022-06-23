import os

from src.bot import TwitchBot
from src.misc import alldata


def main():
    alldata.init()
    bot = TwitchBot()
    bot.run()


if __name__ == "__main__":
    environment: str = os.environ.get("env", "")
    try:
        if((environment == "dev") or (environment == "prod")):
            main()
        else:
            raise TypeError("Only 2 types are allow (dev/production)")

    except Exception as msg:
        print(msg)
