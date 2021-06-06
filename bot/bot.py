from twitchio.ext import commands

class TwitchBot(commands.Bot,):
    def __init__(self,environment):

        self.environment = environment

        try:
            if(environment == "dev"):
                print("Init bot on DEVELOPMENT environment")
                with open ("./data/dev_env", "r", encoding="utf-8") as f:
                    IRC_TOKEN, API_TOKEN, self.NICK, self.CHANNELS = (l.strip() for l in f.readlines())
                super().__init__(
                    irc_token = IRC_TOKEN,
                    api_token = API_TOKEN,
                    client_id = "uej04g8lskt59abzr5o50lt67k9kmi",
                    prefix = "!", 
                    nick = self.NICK,
                    initial_channels = [self.CHANNELS],
                )

            elif(environment == "prod"):
                print("Init bot on PRODUCTION environment")
                with open ("./data/env", "r", encoding="utf-8") as f:
                    IRC_TOKEN, API_TOKEN, self.NICK, self.CHANNELS = (l.strip() for l in f.readlines())

                super().__init__(
                    irc_token = IRC_TOKEN,
                    api_token = API_TOKEN,
                    client_id = "uej04g8lskt59abzr5o50lt67k9kmi",
                    prefix = "!", 
                    nick = self.NICK,
                    initial_channels = [self.CHANNELS],
                )
            print("Done")
        except (FileNotFoundError):
            msg = "Sorry you DON'T HAVE PERMISSION to run on production."
            raise TypeError(msg)

        except Exception as e:
            msg = "start bot fail with error \"" + str(e) + "\" try check your ... first "
            raise TypeError(msg)
            
    async def event_ready(self):
        print("Bot joining channel.")
        self.channel = self.get_channel(self.CHANNELS)
        await self.channel.send(self.NICK + " is joined the channels.")
        print("Joined")