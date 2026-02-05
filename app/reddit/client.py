import praw
from app.config import get_settings
from typing import List

settings = get_settings()


class RedditClient:
    """Wrapper for Reddit API client."""

    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent
        )

    def get_subreddit(self, subreddit_name: str):
        """Get subreddit instance."""
        return self.reddit.subreddit(subreddit_name)

    def get_hot_posts(self, subreddit_name: str, limit: int = 100):
        """Fetch hot posts from a subreddit."""
        subreddit = self.get_subreddit(subreddit_name)
        return subreddit.hot(limit=limit)

    def get_top_posts(self, subreddit_name: str, time_filter: str = "day", limit: int = 100):
        """Fetch top posts from a subreddit."""
        subreddit = self.get_subreddit(subreddit_name)
        return subreddit.top(time_filter=time_filter, limit=limit)

    def get_post_comments(self, post, limit: int = 10):
        """Get top comments from a post."""
        post.comments.replace_more(limit=0)  # Remove "more comments" instances
        return post.comments.list()[:limit]


def get_reddit_client() -> RedditClient:
    """Get Reddit client instance."""
    return RedditClient()
