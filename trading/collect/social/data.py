from datetime import datetime
from enum import Enum


class SocialMedia(Enum):
    TWITTER = "TWITTER"


class SocialMediaPost:
    social_media: SocialMedia
    url: str
    author: str
    date: datetime
    text: str
