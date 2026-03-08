# Imports
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import enum

# Base class for all models
Base = declarative_base()

# Database connection
engine = create_engine("sqlite:///vault.db", echo=True)

# Session maker
SessionLocal = sessionmaker(bind=engine)


# Role Enum
class UserRole(enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)

    username = Column(String(50), unique=True, nullable=False)

    email = Column(String(100), unique=True, nullable=False)

    password_hash = Column(String(255), nullable=False)

    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User id={self.id} username={self.username} role={self.role.value}>"