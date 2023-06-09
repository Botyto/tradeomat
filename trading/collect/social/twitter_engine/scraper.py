import datetime
import json
import typing

from collect.web import HttpClient
from collect.social.twitter_engine.data import Tweet, TwitterUser


class TwitterScraper:
    AUTHORIZATION = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
    client: HttpClient
    guest_token: str|None = None

    def __init__(self, client: HttpClient|None = None, warmup: bool = False):
        self.client = client or HttpClient()
        if warmup:
            self.warmup()

    def warmup(self):
        self._get_guest_token()

    def _get_guest_token(self):
        if self.guest_token is None:
            found_response = self.client.get("https://twitter.com/explore")
            html = found_response.text
            gt_from = html.index("gt=")
            gt_to = html.index(";", gt_from)
            self.guest_token = html[gt_from+3:gt_to]
        return self.guest_token

    def _api_call(self, url: str):
        headers = {
            "Authorization": self.AUTHORIZATION,
            "x-guest-token": self._get_guest_token(),
        }
        response = self.client.get(url, headers=headers)
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
        user_id = self.get_user(username).rest_id
        result = []
        cursor = None
        if min_date:
            while True:
                chunk, cursor = self._get_tweets_page(user_id, cursor=cursor)
                result.extend(chunk)
                if not chunk or chunk[-1].created_at < min_date:
                    break
                if max_count and len(result) >= max_count:
                    break
                if not cursor:
                    break
        elif max_count:
            while len(result) < max_count:
                chunk, cursor = self._get_tweets_page(user_id, count=max_count-len(result), cursor=cursor)
                result.extend(chunk)
                if not chunk:
                    break
        else:
            result, _ = self._get_tweets_page(user_id)
        if max_count and len(result) > max_count:
            result = result[:max_count]
        return result

    def _get_tweets_page(self, user_id: str, count: int = 100, cursor: str|None = None) -> typing.Tuple[typing.List[Tweet], str|None]:
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
