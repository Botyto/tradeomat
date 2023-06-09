from collect.engine import BaseReader, BaseWriter
from datetime import datetime
import itertools
import os
import pickle
import typing

from collect.social.data import SocialMedia, SocialMediaPost


class SocialReader(BaseReader):
    def latest_date(self, username: str) -> datetime:
        pass


class SocialWriter(BaseWriter):
    def _get_path(self, media: SocialMedia, author: str):
        return self.get_ns_data_path(str(media), author + ".pickle")

    def store(self, post: SocialMediaPost):
        self.store_many([post])

    def store_many(self, posts: typing.List[SocialMediaPost]):
        by_media = itertools.groupby(posts, lambda p: p.media)
        for media, media_posts in by_media:
            by_author = itertools.groupby(media_posts, lambda p: p.author)
            for author, author_posts in by_author:
                path = self._get_path(media, author)
                # append
                all_posts = []
                if os.path.isfile(path):
                    with open(path, "rb") as f:
                        all_posts: typing.List[SocialMediaPost] = pickle.load(f)
                all_posts.extend(author_posts)
                with open(path, "wb") as f:
                    pickle.dump(all_posts, f)
