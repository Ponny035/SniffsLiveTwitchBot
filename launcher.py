from bot import TwitchBot, UserFunction
import sys

def main(environment):
    userfunction = UserFunction()
    bot = TwitchBot(environment,userfunction)
    bot.run()

if __name__ == "__main__":
    environment = sys.argv[1]
    try:
        if((environment == "dev") or (environment == "prod")):
            main(environment)
        else:
            raise TypeError("Only 2 types are allow (dev/production)")

    except Exception as msg:
        print(msg)
