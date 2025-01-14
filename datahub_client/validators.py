from datetime import datetime


def check_timestamp_is_in_the_past(datetime: datetime) -> datetime:
    if datetime is not None and datetime.timestamp() >= datetime.now().timestamp():
        raise ValueError("timestamp must be in the past")
    return datetime
