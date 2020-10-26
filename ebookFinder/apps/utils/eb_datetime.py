# -*- coding:utf-8 -*-

import datetime
import pytz

local_tz = pytz.timezone('Asia/Seoul')


def set_timezone(data, tz=local_tz):
    if data.tzinfo is None:
        return tz.localize(data)
    else:
        return data.astimezone(local_tz)


def tz_now(tz=local_tz):
    return set_timezone(datetime.datetime.now(), tz=tz)
