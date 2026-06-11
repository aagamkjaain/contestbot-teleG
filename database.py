from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import DATABASE_URL

# Create engine and session
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    """Telegram user model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")


class Contest(Base):
    """Contest model from CLIST API"""
    __tablename__ = "contests"
    
    id = Column(Integer, primary_key=True)
    clist_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # in seconds
    url = Column(String, nullable=False)
    difficulty = Column(String, nullable=True)  # Easy, Medium, Hard
    fetched_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    reminders = relationship("Reminder", back_populates="contest", cascade="all, delete-orphan")


class Reminder(Base):
    """User reminder preferences"""
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=False)
    minutes_before = Column(Integer, default=30)  # Remind 30 minutes before
    sent = Column(Boolean, default=False)  # Whether reminder was already sent
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="reminders")
    contest = relationship("Contest", back_populates="reminders")


class Subscription(Base):
    """Platform subscriptions for users"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String, nullable=False)  # Codeforces, LeetCode, etc.
    subscribed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(engine)


def get_session():
    """Get a new database session"""
    return Session()
