from datetime import datetime, timezone, timedelta

def std_str(date):
    return date.strftime("%Y/%m/%d")

def arxiv_str(date):
    return date.strftime("%Y%m%d")

def today():
    return datetime.now(timezone.utc)

def yesterday():
    today = datetime.now(timezone.utc)
    return (today - timedelta(days=1))
