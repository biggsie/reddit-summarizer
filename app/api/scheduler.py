from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.database import SessionLocal
from app.reddit.fetcher import RedditFetcher
from app.ai.summarizer import PostSummarizer
from app.email.sender import EmailSender
from app.models import UserPreferences
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_scheduled_digest():
    """
    Job function to send daily digest.
    Called by scheduler at configured time.
    """
    logger.info("Starting scheduled digest generation...")

    db = SessionLocal()
    try:
        # Get preferences
        prefs = db.query(UserPreferences).first()
        if not prefs:
            logger.error("No preferences found")
            return

        # Fetch posts
        fetcher = RedditFetcher(db)
        posts = fetcher.get_top_posts(count=prefs.posts_per_digest)

        if not posts:
            logger.info("No new posts found for digest")
            return

        logger.info(f"Found {len(posts)} posts for digest")

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

            logger.info(f"Digest sent successfully to {prefs.email_address}")
        else:
            logger.error("Failed to send digest email")

    except Exception as e:
        logger.error(f"Error in scheduled digest: {e}")
    finally:
        db.close()


def start_scheduler():
    """Initialize and start the background scheduler."""
    scheduler = BackgroundScheduler()

    # Get digest time from settings (default 06:00)
    from app.config import get_settings
    settings = get_settings()
    hour, minute = settings.digest_time.split(":")

    # Schedule daily digest
    scheduler.add_job(
        send_scheduled_digest,
        trigger=CronTrigger(hour=int(hour), minute=int(minute)),
        id="daily_digest",
        name="Send daily Reddit digest",
        replace_existing=True
    )

    scheduler.start()
    logger.info(f"Scheduler started. Digest will be sent daily at {settings.digest_time}")

    return scheduler
