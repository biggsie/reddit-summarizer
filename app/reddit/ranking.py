import time
from typing import List
from app.models import RankedPost
import math


class PostRanker:
    """Ranks Reddit posts using custom algorithm."""

    def __init__(self):
        self.current_time = time.time()

    def calculate_velocity(self, post) -> float:
        """
        Calculate upvotes per hour to catch trending content early.
        Higher velocity = more rapidly gaining upvotes.
        """
        age_hours = (self.current_time - post.created_utc) / 3600
        if age_hours < 0.1:  # Prevent division by very small numbers
            age_hours = 0.1
        velocity = post.score / age_hours
        return velocity

    def calculate_engagement_quality(self, post) -> float:
        """
        Calculate comment-to-upvote ratio.
        Higher ratio = more discussion relative to upvotes.
        """
        if post.score == 0:
            return 0
        ratio = post.num_comments / post.score
        # Normalize to 0-1 range, considering typical ratios
        # Most posts have 0.01-0.1 ratio
        normalized = min(ratio * 10, 1.0)
        return normalized

    def calculate_popularity_percentile(self, post, all_posts_in_subreddit: List) -> float:
        """
        Calculate percentile ranking within subreddit.
        Where does this post rank among all posts from same subreddit?
        """
        if not all_posts_in_subreddit:
            return 0.5

        subreddit_posts = [p for p in all_posts_in_subreddit if p.subreddit.display_name == post.subreddit.display_name]
        if not subreddit_posts:
            return 0.5

        scores = sorted([p.score for p in subreddit_posts], reverse=True)
        try:
            position = scores.index(post.score)
            percentile = 1 - (position / len(scores))
        except ValueError:
            percentile = 0.5

        return percentile

    def calculate_title_quality(self, title: str) -> float:
        """
        Assess title quality based on various signals.
        Good titles are informative, not clickbait.
        """
        score = 0.5  # Base score

        # Length scoring (prefer moderate length)
        word_count = len(title.split())
        if 5 <= word_count <= 20:
            score += 0.2
        elif word_count < 5:
            score -= 0.1

        # Penalize excessive punctuation (clickbait indicator)
        exclamation_count = title.count('!')
        question_count = title.count('?')
        if exclamation_count > 1 or question_count > 1:
            score -= 0.2

        # Penalize ALL CAPS
        if title.isupper() and len(title) > 10:
            score -= 0.3

        # Bonus for proper capitalization
        if title[0].isupper() and not title.isupper():
            score += 0.1

        return max(0, min(1, score))

    def calculate_content_type_score(self, post) -> float:
        """
        Score based on content type.
        Self posts (text) often have more substance.
        """
        if post.is_self:
            # Self post with substantial text
            if hasattr(post, 'selftext') and len(post.selftext) > 200:
                return 0.8
            return 0.5
        else:
            # Link post
            return 0.4

    def rank_post(self, post, all_posts: List) -> float:
        """
        Calculate overall rank score for a post.
        Combines multiple signals with weights.
        """
        # Calculate individual components
        velocity = self.calculate_velocity(post)
        engagement = self.calculate_engagement_quality(post)
        approval = post.upvote_ratio if hasattr(post, 'upvote_ratio') else 0.5
        percentile = self.calculate_popularity_percentile(post, all_posts)
        title_quality = self.calculate_title_quality(post.title)
        content_score = self.calculate_content_type_score(post)

        # Normalize velocity (log scale to handle wide range)
        velocity_normalized = min(math.log10(velocity + 1) / 4, 1.0)

        # Weighted combination
        weights = {
            'velocity': 0.25,
            'engagement': 0.20,
            'approval': 0.20,
            'percentile': 0.15,
            'title': 0.10,
            'content': 0.10
        }

        rank_score = (
            weights['velocity'] * velocity_normalized +
            weights['engagement'] * engagement +
            weights['approval'] * approval +
            weights['percentile'] * percentile +
            weights['title'] * title_quality +
            weights['content'] * content_score
        )

        return rank_score

    def rank_posts(self, posts: List) -> List[RankedPost]:
        """
        Rank a list of posts and return sorted by score.
        """
        posts_list = list(posts)  # Convert generator to list
        ranked = []

        for post in posts_list:
            score = self.rank_post(post, posts_list)

            ranked_post = RankedPost(
                post_id=post.id,
                subreddit=post.subreddit.display_name,
                title=post.title,
                url=f"https://reddit.com{post.permalink}",
                score=post.score,
                num_comments=post.num_comments,
                upvote_ratio=post.upvote_ratio if hasattr(post, 'upvote_ratio') else 0.0,
                created_utc=post.created_utc,
                rank_score=score,
                selftext=post.selftext if hasattr(post, 'selftext') else None,
                is_self=post.is_self
            )
            ranked.append(ranked_post)

        # Sort by rank score descending
        ranked.sort(key=lambda x: x.rank_score, reverse=True)

        return ranked

    def select_diverse_posts(self, ranked_posts: List[RankedPost], count: int) -> List[RankedPost]:
        """
        Select posts using round-robin to ensure diverse subreddit representation.
        """
        if len(ranked_posts) <= count:
            return ranked_posts

        # Group by subreddit
        by_subreddit = {}
        for post in ranked_posts:
            if post.subreddit not in by_subreddit:
                by_subreddit[post.subreddit] = []
            by_subreddit[post.subreddit].append(post)

        # Round-robin selection
        selected = []
        subreddits = list(by_subreddit.keys())
        index = 0

        while len(selected) < count:
            current_subreddit = subreddits[index % len(subreddits)]

            if by_subreddit[current_subreddit]:
                selected.append(by_subreddit[current_subreddit].pop(0))

            index += 1

            # If we've exhausted all subreddits, break
            if all(len(posts) == 0 for posts in by_subreddit.values()):
                break

        return selected
