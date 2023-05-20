import datetime
import json
import requests
import typing


class TwitterUser:
    rest_id: str
    username: str
    display_name: str
    tweets_count: int
    followers_count: int
    created_at: datetime.datetime

    def __init__(self, rest_id: int, username: str, display_name: str, tweets_count: int, followers_count: int, created_at: datetime.datetime):
        self.rest_id = rest_id
        self.username = username
        self.display_name = display_name
        self.tweets_count = tweets_count
        self.followers_count = followers_count
        self.created_at = created_at

    def __eq__(self, rhs):
        return isinstance(rhs, TwitterUser) and self.rest_id == rhs.rest_id
    
    def __hash__(self):
        return hash(self.rest_id)


class Tweet:
    id: str
    created_at: datetime.datetime
    text: str
    likes: int
    retweets: int

    def __init__(self, id, created_at, text, likes, retweets):
        self.id = id
        self.created_at = created_at
        self.text = text
        self.likes = likes
        self.retweets = retweets

    def __eq__(self, rhs):
        return isinstance(rhs, Tweet) and self.id == rhs.id

    def __hash__(self):
        return hash(self.id)


class TwitterScraper:
    AUTHORIZATION = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

    _session: requests.Session
    _guest_token: str|None = None
    _thorttle: datetime.timedelta|None = None

    def __init__(self, warmup: bool = False, user_agent: str|None = None, throttle: datetime.timedelta|None = None):
        self._session = requests.Session()
        if user_agent is not None:
            self._session.headers.update({"User-Agent": user_agent})
        self._throttle = throttle
        if warmup:
            self.warmup()

    def warmup(self):
        self._get_guest_token()

    def _get_guest_token(self):
        if self._guest_token is None:
            found_response = self._session.get("https://twitter.com/explore")
            html = found_response.text
            gt_from = html.index("gt=")
            gt_to = html.index(";", gt_from)
            self._guest_token = html[gt_from+3:gt_to]
        return self._guest_token

    def _api_call(self, url: str):
        headers = {
            "Authorization": self.AUTHORIZATION,
            "x-guest-token": self._get_guest_token(),
        }
        response = self._session.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_user(self, username: str) -> TwitterUser:
        variables = {
            "screen_name": username,
            "withSafetyModeUserFields": True,
        }
        features = {
            "blue_business_profile_image_shape_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "highlights_tweets_tab_ui_enabled": True,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
        }
        url = f"https://twitter.com/i/api/graphql/pVrmNaXcxPjisIvKtLDMEA/UserByScreenName?variables={json.dumps(variables)}&features={json.dumps(features)}"
        response = self._api_call(url)
        rest_id = response["data"]["user"]["result"]["rest_id"]
        legacy_user = response["data"]["user"]["result"]["legacy"]
        return TwitterUser(
            rest_id,
            username,
            legacy_user["name"],
            legacy_user["statuses_count"],
            legacy_user["followers_count"],
            datetime.datetime.strptime(legacy_user["created_at"], "%a %b %d %H:%M:%S %z %Y"),
        )

    def get_tweets(self, username: str, max_count: int|None = None, min_date: datetime.datetime|None = None):
        result = []
        cursor = None
        if min_date:
            while True:
                chunk, cursor = self._get_tweets_page(username, cursor=cursor)
                result.extend(chunk)
                if not chunk or chunk[-1].created_at < min_date:
                    break
                if max_count and len(result) >= max_count:
                    break
                if not cursor:
                    break
        elif max_count:
            while len(result) < max_count:
                chunk, cursor = self._get_tweets_page(username, count=max_count-len(result), cursor=cursor)
                result.extend(chunk)
                if not chunk:
                    break
        else:
            result, _ = self._get_tweets_page(username)
        if max_count and len(result) > max_count:
            result = result[:max_count]
        return result

    def _get_tweets_page(self, username: str, count: int = 100, cursor: str|None = None) -> typing.Tuple[typing.List[Tweet], str|None]:
        user_id = self.get_user(username).rest_id
        variables = {
            "userId": user_id,
            "count": count,
            "includePromotedContent": False,
            "withQuickPromoteEligibilityTweetFields": False,
            "withVoice": False,
            "withV2Timeline": True,
        }
        if cursor:
            variables["cursor"] = cursor
        features = {
            "rweb_lists_timeline_redesign_enabled": False,
            "blue_business_profile_image_shape_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "tweetypie_unmention_optimization_enabled": True,
            "vibe_api_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
            "interactive_text_enabled": True,
            "responsive_web_text_conversations_enabled": False,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": False,
            "responsive_web_enhance_cards_enabled": False,
        }
        url = f"https://twitter.com/i/api/graphql/WzJjibAcDa-oCjCcLOotcg/UserTweets?variables={json.dumps(variables)}&features={json.dumps(features)}"
        response = self._api_call(url)
        instructions = response["data"]["user"]["result"]["timeline_v2"]["timeline"]["instructions"]
        result = []
        cursor = None
        for instr in instructions:
            if instr["type"] != "TimelineAddEntries":
                continue
            for entry in instr["entries"]:
                content = entry["content"]
                if content["entryType"] == "TimelineTimelineItem":
                    tweet_id = entry["entryId"]
                    timeline_content = content["itemContent"]
                    tweet_raw = timeline_content["tweet_results"]["result"]
                    legacy_tweet = tweet_raw["legacy"]
                    result.append(Tweet(
                        id=tweet_id,
                        created_at=datetime.datetime.strptime(legacy_tweet["created_at"], "%a %B %d %H:%M:%S %z %Y"),
                        text=legacy_tweet["full_text"],
                        likes=legacy_tweet["favorite_count"],
                        retweets=legacy_tweet["retweet_count"],
                    ))
                elif content["entryType"] == "TimelineTimelineCursor" and content["cursorType"] == "Bottom":
                    cursor = content["value"]
        return result, cursor


class BaseCachedTwitterScraper(TwitterScraper):
    tweet_cache_lifetime = datetime.timedelta(hours=1)
    user_cache_lifetime = datetime.timedelta(days=1)

    def __init__(self, warmup=False, user_agent: str|None = None, throttle: datetime.timedelta|None = None):
        super().__init__(warmup, user_agent, throttle)
        self._setup()

    def _setup(self):
        pass

    def delete_all(self):
        pass

    def _try_load_user(self, username: str) -> typing.Tuple[TwitterUser|None, datetime.datetime]:
        return None, datetime.datetime.min

    def _store_user(self, username: str, user: TwitterUser):
        pass

    def get_user(self, username: str) -> TwitterUser:
        user, cached_at = self._try_load_user(username)
        if not user or datetime.datetime.now() - cached_at > self.user_cache_lifetime:
            user = super().get_user(username)
            self._store_user(username, user)
        return user

    def _try_load_tweets_recent(self, username: str) -> typing.Tuple[typing.List[Tweet], datetime.datetime]:
        return [], datetime.datetime.min
    
    def _try_load_tweets_count(self, username: str, count: int) -> typing.Tuple[typing.List[Tweet], datetime.datetime]:
        return [], datetime.datetime.min

    def _try_load_tweets_since(self, username: str, max_count: int, min_date: datetime.datetime) -> typing.Tuple[typing.List[Tweet], datetime.datetime]:
        return [], datetime.datetime.min

    def _try_load_tweets(self, username: str, max_count: int|None = None, min_date: datetime.datetime|None = None) -> typing.Tuple[typing.List[Tweet], datetime.datetime]:
        if min_date:
            return self._try_load_tweets_since(username, max_count, min_date)
        elif max_count:
            return self._try_load_tweets_count(username, max_count)
        else:
            return self._try_load_tweets_recent(username)

    def _store_tweets(self, username: str, tweets: typing.List[Tweet]):
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
    _users: typing.Dict[str, typing.Tuple[TwitterUser, datetime.datetime]]
    _tweets: typing.Dict[str, typing.Tuple[typing.List[Tweet], datetime.datetime]]

    def _setup(self):
        self._users = {}
        self._tweets = {}

    def delete_all(self):
        self._setup()

    def _try_load_user(self, username: str) -> typing.Tuple[TwitterUser|None, datetime.datetime]:
        return self._users.get(username, (None, datetime.datetime.min))

    def _store_user(self, username: str, user: TwitterUser):
        self._users[username] = (user, datetime.datetime.now())

    def _try_load_tweets_recent(self, username: str) -> typing.Tuple[typing.List[Tweet], datetime.datetime]:
        return self._tweets.get(username, ([], datetime.datetime.min))
    
    def _try_load_tweets_count(self, username: str, count: int) -> typing.Tuple[typing.List[Tweet], datetime.datetime]:
        tweets, cached_at = self._tweets.get(username, ([], datetime.datetime.min))
        if len(tweets) >= count:
            tweets = tweets[:count]
        return tweets, cached_at

    def _find_first_tweet_after(self, tweets: typing.List[Tweet], date: datetime.datetime):
        left, right = 0, len(tweets) - 1
        while left <= right:
            mid = (left + right) // 2
            if tweets[mid].created_at < date:
                left = mid + 1
            else:
                right = mid - 1
        if left < len(tweets):
            return left

    def _try_load_tweets_since(self, username: str, max_count: int, min_date: datetime.datetime) -> typing.Tuple[typing.List[Tweet], datetime.datetime]:
        tweets, cached_at = self._tweets.get(username, ([], datetime.datetime.min))
        if not tweets:
            return tweets, cached_at
        if len(tweets) >= max_count:
            tweets = tweets[:max_count]
        cutoff_idx = self._find_first_tweet_after(tweets, min_date)
        if cutoff_idx is not None:
            tweets = tweets[:cutoff_idx]
        return tweets, cached_at

    def _store_tweets(self, username: str, tweets: typing.List[Tweet]):
        cache, _ = self._tweets.get(username, ([], datetime.datetime.min))
        cache.extend(tweets)
        cache.sort(key=lambda t: t.created_at)
        self._tweets[username] = (cache, datetime.datetime.now())
