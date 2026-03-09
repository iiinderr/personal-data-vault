# imports
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import enum


# base class
Base = declarative_base()

# database engine
engine = create_engine("sqlite:///vault.db", echo=True)

# session
SessionLocal = sessionmaker(bind=engine)


# enum for roles
class UserRole(enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


# -------------------------
# USER MODEL
# -------------------------

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

    # relationships
    notes = relationship("EncryptedNote", back_populates="owner", cascade="all, delete-orphan")

    documents = relationship("DocumentMetadata", back_populates="owner", cascade="all, delete-orphan")

    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User id={self.id} username={self.username} role={self.role.value}>"


# -------------------------
# ENCRYPTED NOTE MODEL
# -------------------------

class EncryptedNote(Base):
    __tablename__ = "encrypted_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)

    title = Column(String(200), nullable=False)

    encrypted_content = Column(Text, nullable=False)

    encryption_key_hint = Column(String(100))

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="notes")

    def __repr__(self):
        return f"<EncryptedNote id={self.id} title={self.title}>"


# -------------------------
# DOCUMENT METADATA MODEL
# -------------------------

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

# -------------------------
# PASSWORD HINT MODEL
# -------------------------

class PasswordHint(Base):
    """
    Stores encrypted hints for user passwords.
    The actual password is never stored here — only a hint that helps the user remember it.
    """

    __tablename__ = "password_hints"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # name of the service (gmail, github, bank etc.)
    service_name = Column(String(200), nullable=False)

    # encrypted hint text
    encrypted_hint = Column(Text, nullable=False)

    # optional login URL
    url = Column(String(500))

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PasswordHint id={self.id} service={self.service_name}>"

# -------------------------
# AUDIT LOG MODEL
# -------------------------

class AuditLog(Base):
    """
    Records important actions in the system such as login,
    creating notes, or deleting documents.
    """

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    action = Column(String(100), nullable=False)

    resource_type = Column(String(50))

    resource_id = Column(Integer)

    details = Column(Text)

    ip_address = Column(String(45))

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog id={self.id} action={self.action} user_id={self.user_id}>"
