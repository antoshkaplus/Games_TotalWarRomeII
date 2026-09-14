import datetime


utc_tz = datetime.timezone.utc
def utc_now(): return datetime.datetime.now(utc_tz)
