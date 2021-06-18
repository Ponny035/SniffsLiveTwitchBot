# SniffsLiveTwitchBot
This is sniffs twitch bot made only for Sniffslive Chanel

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

And use `docker-compose.yml` to start Sniffsbot system `docker-compose up`

## Songfeed

To access songfeed please edit `api/rootfs/app/static/fetchapi.css` and change `fetchUrl` and `webSocketUrl` to your localserver
Server is bind on `http://{domain|localhost}:{port|default:8000}/`
