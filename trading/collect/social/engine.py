from collect.engine import BaseReader, BaseWriter
from datetime import datetime
import typing

from collect.social.data import SocialMediaPost


class SocialReader(BaseReader):
    def latest_date(self, username: str) -> datetime:
        pass


class SocialWriter(BaseWriter):
    def store(self, post: SocialMediaPost):
        self.store_many([post])

    def store_many(self, posts: typing.List[SocialMediaPost]):
        pass
