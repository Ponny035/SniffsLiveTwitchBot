from src.timefn.timestamp import get_timestamp


# init variable
command_cooldown = {}
default_cooldown = 20


# cooldown related system
def set_cooldown(username, command):
    now = get_timestamp()
    try:
        command_cooldown[username][command] = now
    except KeyError:
        command_cooldown[username] = {}
        command_cooldown[username][command] = now


def check_cooldown(username, command, cooldown=None):
    if cooldown is None:
        cooldown = default_cooldown
    try:
        timestamp = command_cooldown[username][command]
        now = get_timestamp()
        diff = (now - timestamp).total_seconds()
        if diff > cooldown:
            return True
        else:
            print(f"[INFO] [{get_timestamp()}] COOLDOWN: {username} COMMAND: {command} DURATION: {cooldown - diff}s")
            return False
    except KeyError:
        return True
