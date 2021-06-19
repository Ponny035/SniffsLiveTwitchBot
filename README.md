# SniffsLiveTwitchBot
This is sniffs twitch bot made only for Sniffslive Channel

## Twitchbot

To run create .env file at root directory and contains these variables:
```
# global environment
env={dev|prod}
msg={msgon|msgoff}

# environment for bot
IRC_TOKEN=
API_TOKEN=
BOTNICK=
CHANNELS=

# environment for db
DB_HOST=
DB_USER=
DB_PASS=
DB_NAME=

```

`docker-compose.yml` should have every require parameter to run bot

To start Sniffsbot system use this command `docker-compose up`

## Songfeed

Songfeed Server is bind on `http://{domain|localhost}:{port|default:8000}/`
