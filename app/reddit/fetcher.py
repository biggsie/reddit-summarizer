from typing import List
from sqlalchemy.orm import Session
from app.reddit.client import RedditClient
from app.reddit.ranking import PostRanker
from app.models import Subreddit, PostCache, RankedPost
from datetime import datetime, timedelta


class RedditFetcher:
    """Fetches and processes Reddit posts."""

    def __init__(self, db: Session):
        self.db = db
        self.client = RedditClient()
        self.ranker = PostRanker()

    def get_active_subreddits(self) -> List[Subreddit]:
        """Get list of enabled subreddits."""
        return self.db.query(Subreddit).filter(Subreddit.enabled == True).all()

    def fetch_posts_from_subreddit(self, subreddit: Subreddit, limit: int = 100):
        """Fetch posts from a single subreddit."""
        try:
            # Fetch hot posts
            posts = self.client.get_hot_posts(subreddit.name, limit=limit)

            # Filter by minimum thresholds
            filtered = []
            for post in posts:
                if (post.score >= subreddit.min_upvotes and
                    post.num_comments >= subreddit.min_comments):
                    # Check if not already sent
                    existing = self.db.query(PostCache).filter(
                        PostCache.post_id == post.id,
                        PostCache.sent == True
                    ).first()

                    if not existing:
                        filtered.append(post)

            return filtered
        except Exception as e:
            print(f"Error fetching from r/{subreddit.name}: {e}")
            return []

    def fetch_all_posts(self) -> List:
        """Fetch posts from all active subreddits."""
        subreddits = self.get_active_subreddits()
        all_posts = []

        for subreddit in subreddits:
            posts = self.fetch_posts_from_subreddit(subreddit)
            all_posts.extend(posts)

        return all_posts

    def get_top_posts(self, count: int = 12) -> List[RankedPost]:
        """
        Fetch, rank, and select top posts for digest.
        Uses round-robin selection for diversity.
        """
        # Fetch all posts
        all_posts = self.fetch_all_posts()

        if not all_posts:
            return []

        # Rank posts
        ranked_posts = self.ranker.rank_posts(all_posts)

        # Select diverse posts using round-robin
        selected_posts = self.ranker.select_diverse_posts(ranked_posts, count)

        # Cache posts
        for post in selected_posts:
            self._cache_post(post)

        return selected_posts

    def _cache_post(self, post: RankedPost):
        """Cache post in database."""
        existing = self.db.query(PostCache).filter(PostCache.post_id == post.post_id).first()

        if not existing:
            cached = PostCache(
                post_id=post.post_id,
                subreddit=post.subreddit,
                title=post.title,
                score=post.score,
                num_comments=post.num_comments,
                url=post.url,
                created_utc=post.created_utc,
                sent=False
            )
            self.db.add(cached)
            self.db.commit()

    def mark_posts_as_sent(self, post_ids: List[str]):
        """Mark posts as sent in cache."""
        self.db.query(PostCache).filter(PostCache.post_id.in_(post_ids)).update(
            {PostCache.sent: True, PostCache.sent_at: datetime.utcnow()},
            synchronize_session=False
        )
        self.db.commit()

    def cleanup_old_cache(self, days: int = 30):
        """Remove old cached posts."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        self.db.query(PostCache).filter(PostCache.fetched_at < cutoff).delete()
        self.db.commit()
