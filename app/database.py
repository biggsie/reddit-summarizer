from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base, UserPreferences
from app.config import get_settings
from typing import Generator

settings = get_settings()

# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables and default data."""
    Base.metadata.create_all(bind=engine)

    # Create default preferences if not exists
    db = SessionLocal()
    try:
        prefs = db.query(UserPreferences).first()
        if not prefs:
            default_prefs = UserPreferences(
                email_address=settings.user_email,
                digest_time=settings.digest_time,
                posts_per_digest=settings.posts_per_digest,
                theme="auto"
            )
            db.add(default_prefs)
            db.commit()
    finally:
        db.close()


def get_db() -> Generator[Session, None, None]:
    """Get database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
