from collections import namedtuple
from typing import Any, List, Optional, Tuple

from tweepy import Media
from tweepy import Response as TweepyResponse
from tweepy import Tweet as TweepyTweet

Response = namedtuple("Response", ["data", "meta", "includes", "errors", "tweets"])


class TweetWrapper:
    class Tweet(TweepyTweet):
        def __init__(self, data: Any, media: List[Media]) -> None:
            super().__init__(data)
            self._media: List[Media] = media

        @property
        def media(self) -> List[Media]:
            return self._media

    def __new__(cls, original_response: TweepyResponse):
        tweets = cls._unwrap_tweets_media(data=original_response.data, includes=original_response.includes)
        return Response(
            data=tweets,
            meta=original_response.meta,
            includes=original_response.includes,
            errors=original_response.errors,
            tweets=tweets,
        )

    @staticmethod
    def _unwrap_tweets_media(data: Any, includes: Any) -> List[Tweet]:
        def __construct_custom_tweet(
            original_tweet: TweepyTweet, media: Optional[List[Media]] = None
        ) -> TweetWrapper.Tweet:
            return TweetWrapper.Tweet(original_tweet.data, media or [])

        ret: List[Tuple[TweepyTweet, List[Media]]] = []
        if not all(isinstance(x, TweepyTweet) for x in data):
            raise TypeError("data must be a list of TweepyTweet")

        media = includes["media"]
        if not media:
            return [__construct_custom_tweet(x) for x in data.tweets]

        for tweet in data:
            if tweet.attachments:
                media_keys = tweet.attachments["media_keys"]
                if not media_keys:
                    ret.append((tweet, []))

                for key in media_keys:
                    media_objects = [m for m in media if key == m.media_key]
                    ret.append((tweet, media_objects))

        return [__construct_custom_tweet(tweet, medias) for tweet, medias in ret]
