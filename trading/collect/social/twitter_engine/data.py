import datetime

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
