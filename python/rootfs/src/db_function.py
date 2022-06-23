from datetime import datetime
import os
import time

from supabase_py import create_client, Client


environment = os.environ.get("env", "")
table = os.environ.get("TABLE", "userinfo_duplicate")

SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SUPABASE_API: str = os.environ.get("SUPABASE_API", "")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_API)


def get_time():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def db_connect():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_API)
        return supabase
    except Exception as msg:
        print(msg)
        time.sleep(5)
        db_connect()


def upsert(userdata: dict):
    userdata['Update_Time'] = get_time()
    resp = supabase.table(table).insert(userdata, upsert=True).execute()
    if resp["status_code"] == 200:
        return "success"
    else:
        return "error"


def bulk_upsert(userdatas: list[dict]):
    updated_time = get_time()
    userdatas = [dict(item, **{'Update_Time': updated_time}) for item in userdatas]
    resp = supabase.table(table).insert(userdatas, upsert=True).execute()
    if resp["status_code"] == 200:
        return "success"
    else:
        return "error"


def retrieve_all():
    resp = supabase.table(table).select("User_Name", "Coin", "Watch_Time", "Sub_Month").execute()
    if resp["status_code"] == 200:
        return resp["data"]
    else:
        return []


def retrieve(username: str):
    resp = supabase.table(table).select("*").eq("User_Name", username.lower()).single().execute()
    if resp["status_code"] == 200:
        return resp["data"]
    else:
        return None


def delete(username: str):
    resp = supabase.table(table).delete().eq("User_Name", username.lower())
    if resp["status_code"] == 200:
        return "success"
    else:
        return "error"
