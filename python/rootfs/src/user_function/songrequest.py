from datetime import datetime
import json
import os
import re
import requests

from src.coin.coin import add_coin
from src.db_function import retrieve
from src.misc.webfeed import user_song_request_feed
from src.timefn.timestamp import get_timestamp


# const variables
sorted_song_list: list = []
song_playing = None
song_feed_on: bool = True

api_host: str = os.environ.get("API_SERVER", "")
api_key: str = os.environ.get("WS_KEY", "")

list_url: str = f"{api_host}/api/songlist"
vote_url: str = f"{api_host}/api/vote"
manage_url: str = f"{api_host}/api/songmanage"


async def user_song_request(content: str, timestamp: datetime, username: str, send_message):
    global sorted_song_list
    global song_playing
    cost = 1
    if song_feed_on:
        sorted_song_list, song_playing = get_song_list_api()
    try:
        song_name = re.search("(?<=\\!sr ).+", content)[0]
    except Exception:
        return False

    test_url1 = re.match("https?://", song_name)
    test_url2 = re.match(r"[A-z]+\.(com|org|in|co|tv|us|be)", song_name)
    test_result = bool(test_url1 or test_url2)
    if test_result:
        await send_message(f"@{username} ไม่อนุญาตให้ใส่ลิงค์นะคะ")
        return False
    if len(song_name) == 1:
        song_id = re.match("[1-5]", song_name)
        if song_id is not None:
            try:
                song_id = int(song_id[0])
                song_name = sorted_song_list[song_id - 1]["songKey"]
            except Exception:
                return False
    userdata = retrieve(username)
    if userdata:
        if userdata["Coin"] >= cost:
            add_coin(username, -cost)
            song_name = song_name.strip()
            song_key = song_name.lower()
            song_request = {
                "songKey": song_key,
                "songName": song_name,
                "vote": 1,
                "ts": datetime.timestamp(timestamp) * 1000
            }
            response = requests.post(vote_url, headers={'Authorization': api_key}, json=song_request)
            if response.status_code == 200:
                response_json = json.loads(response.content)
                sorted_song_list = response_json["songList"]
                try:
                    song_playing = response_json["nowPlaying"]
                except KeyError:
                    song_playing = None
                await send_message(f"@{username} ใช้ {cost} sniffscoin โหวตเพลง {response_json['songName']} sniffsMic คะแนนรวม {response_json['songVote']} คะแนน")
                user_song_request_feed(username, song_name, userdata["Coin"] - cost)
                return True
            elif response.status_code == 404:
                print(f"[SONG] [{get_timestamp()}] {song_name} Error connecting to API")
                return False
        else:
            return False
    else:
        return False


async def now_playing(username: str, send_message):
    global sorted_song_list
    global song_playing
    sorted_song_list, song_playing = get_song_list_api()
    if song_playing is not None:
        await send_message(f"@{username} สนิฟกำลังร้องเพลง {song_playing['songName']} น้า sniffsMic sniffsMic sniffsMic")


def get_song_list_api():
    response = requests.get(list_url, headers={'Authorization': api_key})
    if response.status_code == 200:
        response_json = json.loads(response.content)
        try:
            sorted_song_list = response_json["songList"]
        except KeyError:
            sorted_song_list = None
        try:
            song_playing = response_json["nowPlaying"]
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
        await send_message("ยังไม่มีเพลงในคิวจ้า sniffsHeart sniffsHeart sniffsHeart")


async def select_song(song_id: str, send_message):
    global sorted_song_list, song_playing
    song_id = int(song_id)
    try:
        if song_feed_on:
            sorted_song_list, song_playing = get_song_list_api()
        song_select = sorted_song_list[song_id - 1]["id"]
        response = requests.post(manage_url, headers={'Authorization': api_key}, json={"id": song_select})
        if response.status_code == 200:
            response_json = json.loads(response.content)
            try:
                sorted_song_list = response_json["songList"]
            except KeyError:
                sorted_song_list = []
            song_playing = response_json["nowPlaying"]
            await send_message(f"สนิฟเลือกเพลง {song_playing['songName']} sniffsMic sniffsMic sniffsMic")
            print(f"[SONG] [{get_timestamp()}] Sniffs choose {song_playing['songName']} Delete this song from list")
        elif response.status_code == 404:
            response_json = json.loads(response.content)
            try:
                sorted_song_list = response_json["songList"]
            except Exception:
                sorted_song_list = []
            try:
                song_playing = response_json["nowPlaying"]
            except KeyError:
                song_playing = None
            await send_message("ไม่มีเพลงนี้น้า sniffsAH")
            print(f"[SONG] [{get_timestamp()}] No song in list // error from api")
    except IndexError:
        await send_message("ไม่มีเพลงนี้น้า sniffsAH")
        print(f"[SONG] [{get_timestamp()}] No song in list // out of range")


async def delete_songlist(send_message):
    global sorted_song_list
    global song_playing
    response = requests.delete(manage_url, headers={'Authorization': api_key}, json={"confirm": True})
    if response.status_code == 200:
        sorted_song_list = []
        response_json = json.loads(response.content)
        try:
            song_playing = response_json["nowPlaying"]
        except KeyError:
            song_playing = None
        await send_message("ล้าง List เพลงให้แล้วต้าวสนิฟ sniffsHeart")
    elif response.status_code == 404:
        print(f"[SONG] [{get_timestamp()}] Error deleting from api")


async def remove_nowplaying(send_message):
    global sorted_song_list
    global song_playing
    response = requests.patch(manage_url, headers={'Authorization': api_key}, json={"confirm": True})
    if response.status_code == 200:
        response_json = json.loads(response.content)
        song_playing = None
        try:
            sorted_song_list = response_json["songList"]
        except KeyError:
            sorted_song_list = []
        await send_message("ลบ Now Playing เพลงให้แล้วต้าวสนิฟ sniffsHeart")
    elif response.status_code == 404:
        print(f"[SONG] [{get_timestamp()}] Error deleting from api")


async def delete_song(song_id: str, send_message):
    global sorted_song_list
    global song_playing
    song_id = int(song_id)
    try:
        if song_feed_on:
            sorted_song_list, song_playing = get_song_list_api()
        song_select = sorted_song_list[song_id - 1]["id"]
        song_name = sorted_song_list[song_id - 1]["songName"]
        response = requests.put(manage_url, headers={'Authorization': api_key}, json={"id": song_select})
        if response.status_code == 200:
            response_json = json.loads(response.content)
            try:
                sorted_song_list = response_json["songList"]
            except KeyError:
                sorted_song_list = []
            try:
                song_playing = response_json["nowPlaying"]
            except KeyError:
                song_playing = None
            await send_message(f"สนิฟลบเพลง {song_name} sniffsHeart")
            print(f"[SONG] [{get_timestamp()}] Sniffs delete {song_name} from list")
        elif response.status_code == 404:
            response_json = json.loads(response.content)
            try:
                sorted_song_list = response_json["songList"]
                song_playing = response_json["nowPlaying"]
            except KeyError:
                sorted_song_list = []
                song_playing = None
            await send_message("ไม่มีเพลงนี้น้า sniffsAH")
            print(f"[SONG] [{get_timestamp()}] No song in list // error from api")
    except IndexError:
        await send_message("ไม่มีเพลงนี้น้า sniffsAH")
        print(f"[SONG] [{get_timestamp()}] No song in list // out of range")


async def song_feed(status, send_message):
    global song_feed_on
    if (not song_feed_on) and status:
        song_feed_on = status
        await send_message("เปิดระบบ Songfeed แล้วจ้า sniffsHeart")
    elif song_feed_on and (not status):
        song_feed_on = status
        await send_message("ปิดระบบ Songfeed แล้วจ้า ใช้ !song list เพื่อดูรายชื่อเพลง sniffsHeart")
