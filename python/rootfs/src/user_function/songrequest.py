from datetime import datetime
import json
import re
import requests

from src.coin.coin import add_coin
from src.misc import alldata
from src.misc.webfeed import user_song_request_feed
from src.timefn.timestamp import get_timestamp


async def user_song_request(content: str, timestamp: datetime, username: str, send_message):
    cost = 1
    if alldata.song_feed_on:
        alldata.sorted_song_list, alldata.song_playing = get_song_list_api()
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
                song_name = alldata.sorted_song_list[song_id - 1]["songKey"]
            except Exception:
                return False
    userdata = next((userdata for userdata in alldata.allusers_stats if userdata["User_Name"] == username), None)
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
            response = requests.post(alldata.vote_url, headers={'Authorization': alldata.WSKEY}, json=song_request)
            if response.status_code == 200:
                response_json = json.loads(response.content)
                alldata.sorted_song_list = response_json["songList"]
                try:
                    alldata.song_playing = response_json["nowPlaying"]
                except KeyError:
                    alldata.song_playing = None
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
    alldata.sorted_song_list, alldata.song_playing = get_song_list_api()
    if alldata.song_playing is not None:
        await send_message(f"@{username} สนิฟกำลังร้องเพลง {alldata.song_playing['songName']} น้า sniffsMic sniffsMic sniffsMic")


def get_song_list_api():
    response = requests.get(alldata.list_url, headers={'Authorization': alldata.WSKEY})
    if response.status_code == 200:
        response_json = json.loads(response.content)
        try:
            alldata.sorted_song_list = response_json["songList"]
        except KeyError:
            alldata.sorted_song_list = None
        try:
            alldata.song_playing = response_json["nowPlaying"]
        except KeyError:
            alldata.song_playing = None
    else:
        alldata.sorted_song_list = None
        alldata.song_playing = None
    return alldata.sorted_song_list, alldata.song_playing


async def get_song_list(send_message):
    alldata.sorted_song_list, alldata.song_playing = get_song_list_api()
    if alldata.sorted_song_list != []:
        max_song_list = min(len(alldata.sorted_song_list), 5)
        for i in range(0, max_song_list):
            await send_message(f"[{i + 1}] {alldata.sorted_song_list[i]['songName']} {alldata.sorted_song_list[i]['vote']} คะแนน")
            print(f"[SONG] [{get_timestamp()}] {i + 1} {alldata.sorted_song_list[i]['songName']} {alldata.sorted_song_list[i]['vote']} point")
    else:
        await send_message("ยังไม่มีเพลงในคิวจ้า sniffsHeart sniffsHeart sniffsHeart")


async def select_song(song_id: str, send_message):
    song_id = int(song_id)
    try:
        if alldata.song_feed_on:
            alldata.sorted_song_list, alldata.song_playing = get_song_list_api()
        song_select = alldata.sorted_song_list[song_id - 1]["id"]
        response = requests.post(alldata.manage_url, headers={'Authorization': alldata.WSKEY}, json={"id": song_select})
        if response.status_code == 200:
            response_json = json.loads(response.content)
            try:
                alldata.sorted_song_list = response_json["songList"]
            except KeyError:
                alldata.sorted_song_list = []
            alldata.song_playing = response_json["nowPlaying"]
            await send_message(f"สนิฟเลือกเพลง {alldata.song_playing['songName']} sniffsMic sniffsMic sniffsMic")
            print(f"[SONG] [{get_timestamp()}] Sniffs choose {alldata.song_playing['songName']} Delete this song from list")
        elif response.status_code == 404:
            response_json = json.loads(response.content)
            try:
                alldata.sorted_song_list = response_json["songList"]
            except Exception:
                alldata.sorted_song_list = []
            try:
                alldata.song_playing = response_json["nowPlaying"]
            except KeyError:
                alldata.song_playing = None
            await send_message("ไม่มีเพลงนี้น้า sniffsAH")
            print(f"[SONG] [{get_timestamp()}] No song in list // error from api")
    except IndexError:
        await send_message("ไม่มีเพลงนี้น้า sniffsAH")
        print(f"[SONG] [{get_timestamp()}] No song in list // out of range")


async def delete_songlist(send_message):
    response = requests.delete(alldata.manage_url, headers={'Authorization': alldata.WSKEY}, json={"confirm": True})
    if response.status_code == 200:
        alldata.sorted_song_list = []
        response_json = json.loads(response.content)
        try:
            alldata.song_playing = response_json["nowPlaying"]
        except KeyError:
            alldata.song_playing = None
        await send_message("ล้าง List เพลงให้แล้วต้าวสนิฟ sniffsHeart")
    elif response.status_code == 404:
        print(f"[SONG] [{get_timestamp()}] Error deleting from api")


async def remove_nowplaying(send_message):
    response = requests.patch(alldata.manage_url, headers={'Authorization': alldata.WSKEY}, json={"confirm": True})
    if response.status_code == 200:
        response_json = json.loads(response.content)
        alldata.song_playing = None
        try:
            alldata.sorted_song_list = response_json["songList"]
        except KeyError:
            alldata.sorted_song_list = []
        await send_message("ลบ Now Playing เพลงให้แล้วต้าวสนิฟ sniffsHeart")
    elif response.status_code == 404:
        print(f"[SONG] [{get_timestamp()}] Error deleting from api")


async def delete_song(song_id: str, send_message):
    song_id = int(song_id)
    try:
        if alldata.song_feed_on:
            alldata.sorted_song_list, alldata.song_playing = get_song_list_api()
        song_select = alldata.sorted_song_list[song_id - 1]["id"]
        song_name = alldata.sorted_song_list[song_id - 1]["songName"]
        response = requests.put(alldata.manage_url, headers={'Authorization': alldata.WSKEY}, json={"id": song_select})
        if response.status_code == 200:
            response_json = json.loads(response.content)
            try:
                alldata.sorted_song_list = response_json["songList"]
            except KeyError:
                alldata.sorted_song_list = []
            try:
                alldata.song_playing = response_json["nowPlaying"]
            except KeyError:
                alldata.song_playing = None
            await send_message(f"สนิฟลบเพลง {song_name} sniffsHeart")
            print(f"[SONG] [{get_timestamp()}] Sniffs delete {song_name} from list")
        elif response.status_code == 404:
            response_json = json.loads(response.content)
            try:
                alldata.sorted_song_list = response_json["songList"]
                alldata.song_playing = response_json["nowPlaying"]
            except KeyError:
                alldata.sorted_song_list = []
                alldata.song_playing = None
            await send_message("ไม่มีเพลงนี้น้า sniffsAH")
            print(f"[SONG] [{get_timestamp()}] No song in list // error from api")
    except IndexError:
        await send_message("ไม่มีเพลงนี้น้า sniffsAH")
        print(f"[SONG] [{get_timestamp()}] No song in list // out of range")
