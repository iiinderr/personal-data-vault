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

    notes = relationship("EncryptedNote", back_populates="owner", cascade="all, delete-orphan")

    documents = relationship("DocumentMetadata", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} username={self.username} role={self.role.value}>"

class DocumentMetadata(Base):
    __tablename__ = "document_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)

    file_name = Column(String(255), nullable=False)

    file_type = Column(String(50))

    file_size = Column(Integer)

    encrypted_file_path = Column(Text, nullable=False)

    tags = Column(String(500))

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="documents")

    def __repr__(self):
        return f"<DocumentMetadata id={self.id} file_name={self.file_name}>"