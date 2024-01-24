from datetime import datetime
from zoneinfo import ZoneInfo

local_tz = ZoneInfo('Asia/Seoul')

def set_timezone(data, tz=local_tz):
    if data.tzinfo is None:
        return data.replace(tzinfo=tz)
    else:
        return data.astimezone(local_tz)

def tz_now(tz=local_tz):
    return set_timezone(datetime.now(), tz=tz)
