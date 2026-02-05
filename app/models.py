from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

Base = declarative_base()


class Subreddit(Base):
    """Subreddit configuration stored in database."""
    __tablename__ = "subreddits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    enabled = Column(Boolean, default=True)
    min_upvotes = Column(Integer, default=50)
    min_comments = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserPreferences(Base):
    """User preferences stored in database."""
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True)
    email_address = Column(String)
    digest_time = Column(String, default="06:00")
    posts_per_digest = Column(Integer, default=12)
    theme = Column(String, default="auto")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PostCache(Base):
    """Cache of posts to avoid duplicates and track sent posts."""
    __tablename__ = "post_cache"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String, unique=True, index=True)
    subreddit = Column(String, index=True)
    title = Column(String)
    score = Column(Integer)
    num_comments = Column(Integer)
    url = Column(String)
    created_utc = Column(Float)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)


# Pydantic models for API
class SubredditCreate(BaseModel):
    name: str
    min_upvotes: int = 50
    min_comments: int = 5


class SubredditResponse(BaseModel):
    id: int
    name: str
    enabled: bool
    min_upvotes: int
    min_comments: int

    class Config:
        from_attributes = True


class PreferencesUpdate(BaseModel):
    email_address: Optional[str] = None
    digest_time: Optional[str] = None
    posts_per_digest: Optional[int] = None
    theme: Optional[str] = None


class PreferencesResponse(BaseModel):
    email_address: str
    digest_time: str
    posts_per_digest: int
    theme: str

    class Config:
        from_attributes = True


class RankedPost(BaseModel):
    """Post with ranking score."""
    post_id: str
    subreddit: str
    title: str
    url: str
    score: int
    num_comments: int
    upvote_ratio: float
    created_utc: float
    rank_score: float
    selftext: Optional[str] = None
    is_self: bool = False


class DigestPost(BaseModel):
    """Post with AI summary for digest."""
    post_id: str
    subreddit: str
    title: str
    url: str
    score: int
    num_comments: int
    summary: str
