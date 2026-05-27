from datetime import datetime, timezone, timedelta

def std_str(date):
    """
    Formats a datetime object as a human-readable date string.

    Args:
        date (datetime): The date to format.

    Returns:
        str: The date formatted as 'YYYY/MM/DD'.
    """
    return date.strftime("%Y/%m/%d")

def arxiv_str(date):
    """
    Formats a datetime object as an ArXiv-compatible date string.

    Args:
        date (datetime): The date to format.

    Returns:
        str: The date formatted as 'YYYYMMDD'.
    """
    return date.strftime("%Y%m%d")

def today():
    """
    Returns the current UTC datetime.

    Returns:
        datetime: The current date and time in the UTC timezone.
    """
    return datetime.now(timezone.utc)

def yesterday():
    """
    Returns the UTC datetime from exactly 24 hours ago.

    Returns:
        datetime: Yesterday's date and time in the UTC timezone.
    """
    today = datetime.now(timezone.utc)
    return (today - timedelta(days=1))
