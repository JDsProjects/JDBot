from __future__ import annotations

from typing import Any, List, Optional, Tuple

from tweepy import Media, Response
from tweepy import Tweet as TweepyTweet


class TweetWrapper(Response):
    class Tweet(TweepyTweet):
        def __init__(self, data: Any, media: List[Media]) -> None:
            super().__init__(data)
            self._media: List[Media] = media

        @property
        def media(self) -> List[Media]:
            return self._media

    def __init__(self, original_response: Response) -> None:
        self.tweets = self._unwrap_tweets_media()
        super().__init__(
            data=self.data,
            includes=original_response.includes,
            meta=original_response.meta,
            errors=original_response.errors,
        )

    def __construct_custom_tweet(self, original_tweet: TweepyTweet, media: Optional[List[Media]] = None) -> Tweet:
        return self.Tweet(original_tweet.data, media or [])

    def _unwrap_tweets_media(self) -> List[Tweet]:
        ret: List[Tuple[TweepyTweet, List[Media]]] = []
        data = self.data
        if not hasattr(data, "tweets"):
            return []

        media = self.includes["media"]
        if not media:
            return [self.__construct_custom_tweet(x) for x in data.tweets]

        for tweet in data.tweets:
            if tweet.attachments:
                media_keys = tweet.attachments["media_keys"]
                if not media_keys:
                    ret.append((tweet, []))

                for key in media_keys:
                    media_objects = [m for m in media if key == m.media_key]
                    ret.append((tweet, media_objects))

        return [self.__construct_custom_tweet(tweet, medias) for tweet, medias in ret]
