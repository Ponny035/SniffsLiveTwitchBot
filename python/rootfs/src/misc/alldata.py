import os
import requests

from twitchio.ext import routines

from src.db_function import retrieve_all, bulk_upsert
from src.timefn.timestamp import get_timestamp


def init():
    global ENVIRONMENT
    global DRYRUN
    global NICK
    global CHANNELS
    global TOKEN
    global APIID
    global APISEC
    global LISTEN
    global HOST
    global CLIENTID
    global CLIENTSECRET

    global WSHOST
    global WSKEY
    global ABLYKEY

    global feed_enable
    global market_open
    global lotto_open
    global raffle_open
    global song_feed_on
    global channel_live
    global channel_live_on
    global request_status
    global first_run
    global discord_link
    global facebook_link
    global youtube_link
    global instagram_link
    global vip_list
    global dev_list

    global list_url
    global vote_url
    global manage_url

    global shooter_cooldown
    global player_lotto_list
    global sorted_song_list
    global song_playing
    global watchtime_session
    global warning_users
    global command_cooldown

    global timestamp
    global allusers_stats
    global users_cache

    # get os environ
    ENVIRONMENT = os.environ.get("env", "")
    DRYRUN = os.environ.get("msg", "msgon")
    NICK = os.environ.get("BOTNICK", "")
    CHANNELS = os.environ.get("CHANNELS", "")
    TOKEN = os.environ.get("IRC_TOKEN", "")
    APIID = os.environ.get("API_ID", "")
    APISEC = os.environ.get("API_TOKEN", "")
    LISTEN = os.environ.get("CBPORT", "")
    HOST = os.environ.get("CBHOST", "")
    CLIENTID = os.environ.get("CLIENT_ID", "")
    CLIENTSECRET = os.environ.get("CLIENT_SECRET", "")

    WSHOST = os.environ.get("API_SERVER", "")
    WSKEY = os.environ.get("WS_KEY", "")

    ABLYKEY = os.environ.get("ABLY_KEY", "")

    # define default variable
    feed_enable = True
    market_open = True
    lotto_open = False
    raffle_open = False
    song_feed_on = True
    channel_live = False
    channel_live_on = 0
    request_status = False
    first_run = True
    discord_link = "https://discord.gg/Q3AMaHQEGU"  # temp link
    facebook_link = "https://www.facebook.com/sniffslive/"
    youtube_link = "https://www.youtube.com/SniffsLive"
    instagram_link = "https://www.instagram.com/musicsn/"
    vip_list = [NICK, CHANNELS, "sirju001", "mafiamojo", "armzi", "moobot", "sniffsbot"]
    dev_list = []

    list_url = f"{WSHOST}/api/songlist"
    vote_url = f"{WSHOST}/api/vote"
    manage_url = f"{WSHOST}/api/songmanage"

    # init function var
    shooter_cooldown = 0
    player_lotto_list = []
    sorted_song_list = []
    song_playing = None
    watchtime_session = {}
    warning_users = {}
    command_cooldown = {}

    # init user data
    timestamp = get_timestamp()
    allusers_stats = retrieve_all()
    users_cache = get_users_list()


def get_users_list():
    global timestamp
    global users_cache
    now = get_timestamp()
    if (now - timestamp).total_seconds() < 60 and not first_run:
        return users_cache
    url_endpoint = f"https://tmi.twitch.tv/group/user/{CHANNELS}/chatters"
    resp = requests.get(url_endpoint)
    if resp.status_code == 200:
        data = resp.json()
        users_cache = [name for key in data['chatters'] for name in data['chatters'][key]]
        timestamp = get_timestamp()
        return users_cache
    else:
        return []


@routines.routine(minutes=60)
async def sync_db():
    if first_run:
        return
    global allusers_stats
    if not channel_live:
        print(f"[_LOG] [{get_timestamp()}] Start Sync DB")
        bulk_upsert(allusers_stats)
        allusers_stats = retrieve_all()
        print(f"[_LOG] [{get_timestamp()}] Successfully Sync DB")
