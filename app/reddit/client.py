import requests
import time
from typing import List, Dict, Any


class RedditPost:
    """Wrapper for Reddit post data from JSON API."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def id(self) -> str:
        return self._data.get('id', '')

    @property
    def title(self) -> str:
        return self._data.get('title', '')

    @property
    def score(self) -> int:
        return self._data.get('score', 0)

    @property
    def num_comments(self) -> int:
        return self._data.get('num_comments', 0)

    @property
    def upvote_ratio(self) -> float:
        return self._data.get('upvote_ratio', 0.0)

    @property
    def created_utc(self) -> float:
        return self._data.get('created_utc', 0.0)

    @property
    def permalink(self) -> str:
        return self._data.get('permalink', '')

    @property
    def url(self) -> str:
        return self._data.get('url', '')

    @property
    def is_self(self) -> bool:
        return self._data.get('is_self', False)

    @property
    def selftext(self) -> str:
        return self._data.get('selftext', '')

    @property
    def subreddit(self):
        """Mock subreddit object with display_name."""
        class Subreddit:
            def __init__(self, name):
                self.display_name = name
        return Subreddit(self._data.get('subreddit', ''))


class RedditComment:
    """Wrapper for Reddit comment data."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def body(self) -> str:
        return self._data.get('body', '')


class RedditClient:
    """
    Wrapper for Reddit JSON API (no authentication needed).
    Uses Reddit's public JSON endpoints.
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'RedditSummarizer/1.0 (Educational project)'
        }
        self.base_url = 'https://www.reddit.com'
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Rate limiting: 1 request per second

    def _rate_limit(self):
        """Simple rate limiting to respect Reddit's limits."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to Reddit with rate limiting."""
        self._rate_limit()

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Reddit: {e}")
            return {'data': {'children': []}}

    def get_subreddit(self, subreddit_name: str):
        """Get subreddit instance (for compatibility)."""
        return subreddit_name

    def get_hot_posts(self, subreddit_name: str, limit: int = 100):
        """Fetch hot posts from a subreddit."""
        url = f'{self.base_url}/r/{subreddit_name}/hot.json'
        params = {'limit': min(limit, 100)}

        data = self._make_request(url, params)
        posts = [RedditPost(child['data']) for child in data.get('data', {}).get('children', [])]

        return posts

    def get_top_posts(self, subreddit_name: str, time_filter: str = "day", limit: int = 100):
        """Fetch top posts from a subreddit."""
        url = f'{self.base_url}/r/{subreddit_name}/top.json'
        params = {'t': time_filter, 'limit': min(limit, 100)}

        data = self._make_request(url, params)
        posts = [RedditPost(child['data']) for child in data.get('data', {}).get('children', [])]

        return posts

    def get_post_comments(self, post, limit: int = 10) -> List[RedditComment]:
        """Get top comments from a post."""
        if isinstance(post, RedditPost):
            url = f'{self.base_url}{post.permalink}.json'
        else:
            # Fallback if post object is different
            return []

        params = {'limit': limit}
        data = self._make_request(url, params)

        # Comments are in the second element of the response
        if len(data) < 2:
            return []

        comment_data = data[1].get('data', {}).get('children', [])
        comments = []

        for child in comment_data[:limit]:
            if child.get('kind') == 't1':  # t1 is a comment
                comments.append(RedditComment(child.get('data', {})))

        return comments


def get_reddit_client() -> RedditClient:
    """Get Reddit client instance."""
    return RedditClient()
