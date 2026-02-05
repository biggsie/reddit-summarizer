from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import (
    Subreddit, SubredditCreate, SubredditResponse,
    UserPreferences, PreferencesUpdate, PreferencesResponse
)
from app.reddit.fetcher import RedditFetcher
from app.ai.summarizer import PostSummarizer
from app.email.sender import EmailSender
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/subreddits", response_model=List[SubredditResponse])
def get_subreddits(db: Session = Depends(get_db)):
    """Get all configured subreddits."""
    subreddits = db.query(Subreddit).all()
    return subreddits


@router.post("/subreddits", response_model=SubredditResponse)
def add_subreddit(subreddit: SubredditCreate, db: Session = Depends(get_db)):
    """Add a new subreddit to track."""
    # Check if already exists
    existing = db.query(Subreddit).filter(Subreddit.name == subreddit.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Subreddit already exists")

    new_subreddit = Subreddit(
        name=subreddit.name,
        min_upvotes=subreddit.min_upvotes,
        min_comments=subreddit.min_comments,
        enabled=True
    )
    db.add(new_subreddit)
    db.commit()
    db.refresh(new_subreddit)
    return new_subreddit


@router.delete("/subreddits/{subreddit_id}")
def delete_subreddit(subreddit_id: int, db: Session = Depends(get_db)):
    """Remove a subreddit."""
    subreddit = db.query(Subreddit).filter(Subreddit.id == subreddit_id).first()
    if not subreddit:
        raise HTTPException(status_code=404, detail="Subreddit not found")

    db.delete(subreddit)
    db.commit()
    return {"status": "deleted"}


@router.patch("/subreddits/{subreddit_id}/toggle")
def toggle_subreddit(subreddit_id: int, db: Session = Depends(get_db)):
    """Enable/disable a subreddit."""
    subreddit = db.query(Subreddit).filter(Subreddit.id == subreddit_id).first()
    if not subreddit:
        raise HTTPException(status_code=404, detail="Subreddit not found")

    subreddit.enabled = not subreddit.enabled
    db.commit()
    db.refresh(subreddit)
    return subreddit


@router.get("/preferences", response_model=PreferencesResponse)
def get_preferences(db: Session = Depends(get_db)):
    """Get user preferences."""
    prefs = db.query(UserPreferences).first()
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return prefs


@router.put("/preferences", response_model=PreferencesResponse)
def update_preferences(updates: PreferencesUpdate, db: Session = Depends(get_db)):
    """Update user preferences."""
    prefs = db.query(UserPreferences).first()
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")

    if updates.email_address is not None:
        prefs.email_address = updates.email_address
    if updates.digest_time is not None:
        prefs.digest_time = updates.digest_time
    if updates.posts_per_digest is not None:
        prefs.posts_per_digest = updates.posts_per_digest
    if updates.theme is not None:
        prefs.theme = updates.theme

    db.commit()
    db.refresh(prefs)
    return prefs


@router.post("/preview")
def generate_preview(db: Session = Depends(get_db)):
    """Generate a preview of the digest without sending."""
    try:
        # Fetch posts
        fetcher = RedditFetcher(db)
        prefs = db.query(UserPreferences).first()
        posts = fetcher.get_top_posts(count=prefs.posts_per_digest)

        if not posts:
            raise HTTPException(status_code=404, detail="No posts found")

        # Generate summaries
        summarizer = PostSummarizer()
        digest_posts = summarizer.summarize_posts(posts)

        return {
            "posts": [post.dict() for post in digest_posts],
            "count": len(digest_posts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-email")
def send_test_email(db: Session = Depends(get_db)):
    """Send a test email."""
    try:
        prefs = db.query(UserPreferences).first()
        sender = EmailSender()
        success = sender.send_test_email(prefs.email_address)

        if success:
            return {"status": "sent", "message": f"Test email sent to {prefs.email_address}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send test email")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-preview")
def send_preview_digest(db: Session = Depends(get_db)):
    """Generate digest and send as preview email."""
    try:
        # Fetch posts
        fetcher = RedditFetcher(db)
        prefs = db.query(UserPreferences).first()
        posts = fetcher.get_top_posts(count=prefs.posts_per_digest)

        if not posts:
            raise HTTPException(status_code=404, detail="No posts found")

        # Generate summaries
        summarizer = PostSummarizer()
        digest_posts = summarizer.summarize_posts(posts)

        # Send email (preview mode - don't mark posts as sent)
        sender = EmailSender()
        success = sender.send_digest(prefs.email_address, digest_posts, is_preview=True)

        if success:
            return {
                "status": "sent",
                "message": f"Preview digest sent to {prefs.email_address}",
                "post_count": len(digest_posts)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send preview digest")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-digest")
def send_daily_digest(db: Session = Depends(get_db)):
    """Generate and send the actual daily digest."""
    try:
        # Fetch posts
        fetcher = RedditFetcher(db)
        prefs = db.query(UserPreferences).first()
        posts = fetcher.get_top_posts(count=prefs.posts_per_digest)

        if not posts:
            return {"status": "no_posts", "message": "No new posts to send"}

        # Generate summaries
        summarizer = PostSummarizer()
        digest_posts = summarizer.summarize_posts(posts)

        # Send email
        sender = EmailSender()
        success = sender.send_digest(prefs.email_address, digest_posts, is_preview=False)

        if success:
            # Mark posts as sent
            post_ids = [post.post_id for post in digest_posts]
            fetcher.mark_posts_as_sent(post_ids)

            # Cleanup old cache
            fetcher.cleanup_old_cache()

            return {
                "status": "sent",
                "message": f"Digest sent to {prefs.email_address}",
                "post_count": len(digest_posts)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send digest")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
