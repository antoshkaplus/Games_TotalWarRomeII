import datetime


utc_tz = datetime.timezone.utc
def utc_now(): return datetime.datetime.now(utc_tz)


def date_to_str(date) -> str:
    return date.strftime("%Y-%m-%d")

