from zoneinfo import ZoneInfo

from ebookFinder.apps.utils.eb_datetime import local_tz, tz_now


def test_tz_now():
    now_with_tz = tz_now()
    assert now_with_tz.tzinfo == local_tz

    custom_tz = ZoneInfo("America/New_York")
    now_with_custom_tz = tz_now(tz=custom_tz)
    assert now_with_custom_tz.tzinfo == custom_tz
