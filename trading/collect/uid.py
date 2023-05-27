from datetime import datetime, timezone
from uuid import uuid4

def new(date: datetime|None) -> str:
    if date is None:
        date = datetime.utcnow()
    else:
        assert date.tzinfo == timezone.utc
    timestamp = int(date.timestamp())
    uuid = str(uuid4())
    uuid_first_part = uuid.split('-')[0]
    return f'{timestamp}_{uuid_first_part}'

def timestamp_of(id: str) -> datetime:
    timestamp = int(id.split('_')[0])
    return datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc)
