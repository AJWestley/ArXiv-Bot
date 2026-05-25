from datetime import datetime, timezone, timedelta

delta_map = {
        0: 3,
        7: 2
    }

def std_str(date):
    return date.strftime("%Y/%m/%d")

def arxiv_str(date):
    return date.strftime("%Y%m%d")

def today():
    return datetime.now(timezone.utc)

def yesterday():
    today = datetime.now(timezone.utc)
    return (today - timedelta(days=1))

def last_weekday():
    today = datetime.now(timezone.utc)
    delta = delta_map.get(today.weekday(), 1)
    return (today - timedelta(days=delta))