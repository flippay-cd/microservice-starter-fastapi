from datetime import UTC, datetime, timezone


def utcnow() -> datetime:
    return datetime.now(tz=UTC)


def to_timezone(dt: datetime | None, tz: timezone = UTC) -> datetime | None:
    if dt:
        if dt.utcoffset() is None:
            return dt.replace(tzinfo=tz)
        return dt.astimezone(tz)

    return None
