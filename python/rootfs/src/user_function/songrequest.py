from datetime import datetime
import json
import re
import requests

from src.coin.coin import add_coin
from src.db_function import DBManager
from src.timefn.timestamp import get_timestamp


# const variables
sorted_song_list = []
song_playing = None
song_feed_on = True

list_url = 'http://api-server:8000/api/v1/songlist'
vote_url = 'http://api-server:8000/api/v1/vote'
select_url = 'http://api-server:8000/api/v1/select'
delete_url = 'http://api-server:8000/api/v1/del'
clear_url = 'http://api-server:8000/api/v1/clear'
rem_url = 'http://api-server:8000/api/v1/rem'

db = DBManager()


async def user_song_request(content, timestamp, username, send_message):
    global sorted_song_list
    global song_playing
    cost = 1
    if song_feed_on:
        sorted_song_list, song_playing = get_song_list_api()
    try:
        song_name = re.search("(?<=\\!sr ).+", content)[0]
    except Exception:
        song_name = None
    if (song_name is not None) and (len(song_name) == 1):
        song_id = re.match("[1-5]", song_name)
        if song_id is not None:
            try:
                song_id = int(song_id[0])
                song_name = sorted_song_list[song_id - 1]["songKey"]
            except Exception:
                return
    if song_name is not None:
        if db.check_exist(username):
            userdata = db.retrieve(username)
            if userdata["coin"] >= cost:
                add_coin(username, -cost)
                song_name = song_name.strip()
                song_key = song_name.lower()
                song_request = {
                    "songKey": song_key,
                    "songName": song_name,
                    "vote": 1,
                    "ts": datetime.timestamp(timestamp) * 1000
                }
                response = requests.post(vote_url, json=song_request)
                if response.status_code == 200:
                    response_json = json.loads(response.content)
                    sorted_song_list = response_json["songlist"]
                    try:
                        song_playing = response_json["nowplaying"]
                    except KeyError:
                        song_playing = None
                    await send_message(f"@{username} ใช้ {cost} sniffscoin โหวตเพลง {response_json['songname']} คะแนนรวม {response_json['songvote']} คะแนน")
                elif response.status_code == 404:
                    print(f"[SONG] [{get_timestamp()}] {song_name} Error connecting to API")


async def now_playing(username, send_message):
    global sorted_song_list
    global song_playing
    sorted_song_list, song_playing = get_song_list_api()
    if song_playing is not None:
        await send_message(f"@{username} สนิฟกำลังร้องเพลง {song_playing['songName']} น้า")


def get_song_list_api():
    response = requests.get(list_url)
    if response.status_code == 200:
        response_json = json.loads(response.content)
        try:
            sorted_song_list = response_json["songlist"]
        except KeyError:
            sorted_song_list = None
        try:
            song_playing = response_json["nowplaying"]
        except KeyError:
            song_playing = None
    else:
        sorted_song_list = None
        song_playing = None
    return sorted_song_list, song_playing


async def get_song_list(send_message):
    global sorted_song_list
    global song_playing
    sorted_song_list, song_playing = get_song_list_api()
    if sorted_song_list != []:
        max_song_list = min(len(sorted_song_list), 5)
        for i in range(0, max_song_list):
            await send_message(f"[{i + 1}] {sorted_song_list[i]['songName']} {sorted_song_list[i]['vote']} คะแนน")
            print(f"[SONG] [{get_timestamp()}] {i + 1} {sorted_song_list[i]['songName']} {sorted_song_list[i]['vote']} point")
    else:
        await send_message("ยังไม่มีเพลงในคิวจ้า")


async def select_song(song_id, send_message):
    global sorted_song_list, song_playing
    song_id = int(song_id)
    try:
        # if we have front end, we need to fetch new list
        if song_feed_on:
            sorted_song_list, song_playing = get_song_list_api()
        song_select = sorted_song_list[song_id - 1]["songKey"]
        response = requests.post(select_url, json={"songKey": song_select})
        if response.status_code == 200:
            response_json = json.loads(response.content)
            try:
                sorted_song_list = response_json["songlist"]
            except KeyError:
                sorted_song_list = []
            song_playing = response_json["nowplaying"]
            await send_message(f"สนิฟเลือกเพลง {song_playing['songName']}")
            print(f"[SONG] [{get_timestamp()}] Sniffs choose {song_playing['songName']} Delete this song from list")
        elif response.status_code == 404:
            response_json = json.loads(response.content)
            try:
                sorted_song_list = response_json["songlist"]
            except Exception:
                sorted_song_list = []
            try:
                song_playing = response_json["nowplaying"]
            except KeyError:
                song_playing = None
            await send_message("ไม่มีเพลงนี้น้า")
            print(f"[SONG] [{get_timestamp()}] No song in list // error from api")
    except IndexError:
        await send_message("ไม่มีเพลงนี้น้า")
        print(f"[SONG] [{get_timestamp()}] No song in list // out of range")


async def delete_songlist(send_message):
    global sorted_song_list
    global song_playing
    response = requests.post(clear_url, json={"confirm": True})
    if response.status_code == 200:
        sorted_song_list = []
        response_json = json.loads(response.content)
        try:
            song_playing = response_json["nowplaying"]
        except KeyError:
            song_playing = None
        await send_message("ล้าง List เพลงให้แล้วต้าวสนิฟ")
    elif response.status_code == 404:
        print(f"[SONG] [{get_timestamp()}] Error deleting from api")


async def remove_nowplaying(send_message):
    global sorted_song_list
    global song_playing
    response = requests.post(rem_url, json={"confirm": True})
    if response.status_code == 200:
        response_json = json.loads(response.content)
        song_playing = None
        try:
            sorted_song_list = response_json["songlist"]
        except KeyError:
            sorted_song_list = []
        await send_message("ลบ Now Playing เพลงให้แล้วต้าวสนิฟ")
    elif response.status_code == 404:
        print(f"[SONG] [{get_timestamp()}] Error deleting from api")


async def delete_song(song_id, send_message):
    global sorted_song_list
    global song_playing
    song_id = int(song_id)
    try:
        # if we have front end, we need to fetch new list
        if song_feed_on:
            sorted_song_list, song_playing = get_song_list_api()
        song_select = sorted_song_list[song_id - 1]["songKey"]
        response = requests.post(delete_url, json={"songKey": song_select})
        if response.status_code == 200:
            response_json = json.loads(response.content)
            try:
                sorted_song_list = response_json["songlist"]
            except KeyError:
                sorted_song_list = []
            try:
                song_playing = response_json["nowplaying"]
            except KeyError:
                song_playing = None
            await send_message(f"สนิฟลบเพลง {song_select}")
            # await self.get_song_list(send_message)
            print(f"[SONG] [{get_timestamp()}] Sniffs delete {song_select} from list")
        elif response.status_code == 404:
            response_json = json.loads(response.content)
            try:
                sorted_song_list = response_json["songlist"]
                song_playing = response_json["nowplaying"]
            except KeyError:
                sorted_song_list = []
                song_playing = None
            await send_message("ไม่มีเพลงนี้น้า")
            print(f"[SONG] [{get_timestamp()}] No song in list // error from api")
    except IndexError:
        await send_message("ไม่มีเพลงนี้น้า")
        print(f"[SONG] [{get_timestamp()}] No song in list // out of range")


async def song_feed(status, send_message):
    global song_feed_on
    if (not song_feed_on) and status:
        song_feed_on = status
        await send_message("เปิดระบบ Songfeed แล้วจ้า")
    elif song_feed_on and (not status):
        song_feed_on = status
        await send_message("ปิดระบบ Songfeed แล้วจ้า ใช้ !song list เพื่อดูรายชื่อเพลง")
