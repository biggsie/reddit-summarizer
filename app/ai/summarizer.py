from anthropic import Anthropic
from app.config import get_settings
from app.models import RankedPost, DigestPost
from app.reddit.client import RedditClient
from typing import List

settings = get_settings()


class PostSummarizer:
    """Uses Claude Haiku to generate post summaries."""

    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.reddit_client = RedditClient()
        self.model = "claude-haiku-4-5-20251001"  # Claude Haiku 4.5

    def _get_post_content(self, post: RankedPost) -> str:
        """Get full post content including top comments."""
        try:
            # Get the actual Reddit post object
            reddit_post = self.reddit_client.reddit.submission(id=post.post_id)

            # Build content string
            content = f"Title: {post.title}\n\n"

            # Add selftext if it's a text post
            if post.is_self and post.selftext:
                content += f"Post Content:\n{post.selftext[:1000]}\n\n"  # Limit to 1000 chars

            # Get top comments
            comments = self.reddit_client.get_post_comments(reddit_post, limit=5)
            if comments:
                content += "Top Comments:\n"
                for i, comment in enumerate(comments[:5], 1):
                    if hasattr(comment, 'body'):
                        comment_text = comment.body[:300]  # Limit each comment
                        content += f"{i}. {comment_text}\n\n"

            return content
        except Exception as e:
            print(f"Error getting post content for {post.post_id}: {e}")
            return f"Title: {post.title}\n\nPost URL: {post.url}"

    def summarize_post(self, post: RankedPost) -> str:
        """Generate AI summary for a single post."""
        content = self._get_post_content(post)

        prompt = f"""Summarize this Reddit post and its discussion in 2-3 concise sentences.
Focus on the key points and main takeaways. Be informative and objective.

{content}

Summary:"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=150,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            summary = message.content[0].text.strip()
            return summary
        except Exception as e:
            print(f"Error summarizing post {post.post_id}: {e}")
            return f"Unable to generate summary. {post.title}"

    def summarize_posts(self, posts: List[RankedPost]) -> List[DigestPost]:
        """Generate summaries for multiple posts."""
        digest_posts = []

        for post in posts:
            summary = self.summarize_post(post)

            digest_post = DigestPost(
                post_id=post.post_id,
                subreddit=post.subreddit,
                title=post.title,
                url=post.url,
                score=post.score,
                num_comments=post.num_comments,
                summary=summary
            )
            digest_posts.append(digest_post)

        return digest_posts

    def summarize_posts_batch(self, posts: List[RankedPost]) -> List[DigestPost]:
        """
        Batch summarization for better efficiency.
        Process multiple posts in a single API call.
        """
        if not posts:
            return []

        # For now, use individual calls for better error handling
        # Can optimize later with batching if needed
        return self.summarize_posts(posts)
