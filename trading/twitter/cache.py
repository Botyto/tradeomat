import datetime
import typing

import twitter.data
import twitter.scraper


class BaseCachedTwitterScraper(twitter.scraper.TwitterScraper):
    tweet_cache_lifetime = datetime.timedelta(hours=1)
    user_cache_lifetime = datetime.timedelta(days=1)

    def __init__(self, warmup=False, user_agent: str|None = None, throttle: datetime.timedelta|None = None):
        super().__init__(warmup, user_agent, throttle)
        self._setup()

    def _setup(self):
        pass

    def delete_all(self):
        pass

    def _try_load_user(self, username: str) -> typing.Tuple[twitter.data.TwitterUser|None, datetime.datetime]:
        return None, datetime.datetime.min

    def _store_user(self, username: str, user: twitter.data.TwitterUser):
        pass

    def get_user(self, username: str) -> twitter.data.TwitterUser:
        user, cached_at = self._try_load_user(username)
        if not user or datetime.datetime.now() - cached_at > self.user_cache_lifetime:
            user = super().get_user(username)
            self._store_user(username, user)
        return user

    def _try_load_tweets_recent(self, username: str) -> typing.Tuple[typing.List[twitter.data.Tweet], datetime.datetime]:
        return [], datetime.datetime.min
    
    def _try_load_tweets_count(self, username: str, count: int) -> typing.Tuple[typing.List[twitter.data.Tweet], datetime.datetime]:
        return [], datetime.datetime.min

    def _try_load_tweets_since(self, username: str, max_count: int, min_date: datetime.datetime) -> typing.Tuple[typing.List[twitter.data.Tweet], datetime.datetime]:
        return [], datetime.datetime.min

    def _try_load_tweets(self, username: str, max_count: int|None = None, min_date: datetime.datetime|None = None) -> typing.Tuple[typing.List[twitter.data.Tweet], datetime.datetime]:
        if min_date:
            return self._try_load_tweets_since(username, max_count, min_date)
        elif max_count:
            return self._try_load_tweets_count(username, max_count)
        else:
            return self._try_load_tweets_recent(username)

    def _store_tweets(self, username: str, tweets: typing.List[twitter.data.Tweet]):
        pass

    def get_tweets(self, username: str, max_count: int|None = None, min_date: datetime.datetime|None = None):
        result, cached_at = self._try_load_tweets(username, max_count, min_date)
        needs_refresh = datetime.datetime.now() - cached_at > self.tweet_cache_lifetime
        if result:
            if needs_refresh:
                fresh_tweets = None
                if min_date and result[-1].created_at >= min_date:
                    fresh_tweets = super().get_tweets(username, max_count, min_date)
                elif max_count and len(result) < max_count:
                    fresh_tweets = super().get_tweets(username, max_count)
                if fresh_tweets:
                    fresh_tweets = set(fresh_tweets)
                    fresh_tweets = fresh_tweets.difference(result)
                if fresh_tweets:
                    self._store_tweets(username, fresh_tweets)
                    result.extend(fresh_tweets)
                    result.sort(key=lambda t: t.created_at)
            return result
        
        result = super().get_tweets(username, max_count, min_date)
        self._store_tweets(username, result)
        return result


class MemoryCachedTwitterScraper(BaseCachedTwitterScraper):
    _users: typing.Dict[str, typing.Tuple[twitter.data.TwitterUser, datetime.datetime]]
    _tweets: typing.Dict[str, typing.Tuple[typing.List[twitter.data.Tweet], datetime.datetime]]

    def _setup(self):
        self._users = {}
        self._tweets = {}

    def delete_all(self):
        self._setup()

    def _try_load_user(self, username: str) -> typing.Tuple[twitter.data.TwitterUser|None, datetime.datetime]:
        return self._users.get(username, (None, datetime.datetime.min))

    def _store_user(self, username: str, user: twitter.data.TwitterUser):
        self._users[username] = (user, datetime.datetime.now())

    def _try_load_tweets_recent(self, username: str) -> typing.Tuple[typing.List[twitter.data.Tweet], datetime.datetime]:
        return self._tweets.get(username, ([], datetime.datetime.min))
    
    def _try_load_tweets_count(self, username: str, count: int) -> typing.Tuple[typing.List[twitter.data.Tweet], datetime.datetime]:
        tweets, cached_at = self._tweets.get(username, ([], datetime.datetime.min))
        if len(tweets) >= count:
            tweets = tweets[:count]
        return tweets, cached_at

    def _find_first_tweet_after(self, tweets: typing.List[twitter.data.Tweet], date: datetime.datetime):
        left, right = 0, len(tweets) - 1
        while left <= right:
            mid = (left + right) // 2
            if tweets[mid].created_at < date:
                left = mid + 1
            else:
                right = mid - 1
        if left < len(tweets):
            return left

    def _try_load_tweets_since(self, username: str, max_count: int, min_date: datetime.datetime) -> typing.Tuple[typing.List[twitter.data.Tweet], datetime.datetime]:
        tweets, cached_at = self._tweets.get(username, ([], datetime.datetime.min))
        if not tweets:
            return tweets, cached_at
        if len(tweets) >= max_count:
            tweets = tweets[:max_count]
        cutoff_idx = self._find_first_tweet_after(tweets, min_date)
        if cutoff_idx is not None:
            tweets = tweets[:cutoff_idx]
        return tweets, cached_at

    def _store_tweets(self, username: str, tweets: typing.List[twitter.data.Tweet]):
        cache, _ = self._tweets.get(username, ([], datetime.datetime.min))
        cache.extend(tweets)
        cache.sort(key=lambda t: t.created_at)
        self._tweets[username] = (cache, datetime.datetime.now())
