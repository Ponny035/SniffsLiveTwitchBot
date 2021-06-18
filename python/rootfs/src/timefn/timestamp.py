from datetime import datetime


def get_timestamp():
    return datetime.utcnow().replace(microsecond=0)


def sec_to_hms(time):
    day = hour = min = sec = 0
    try:
        day = int(time / 86400)
        hour = int((time / 3600) - (24 * day))
        min = int((time / 60) - (60 * hour) - (60 * 24 * day))
        sec = int(time % 60)
    except Exception as msg:
        print(msg)
    return [day, hour, min, sec]
