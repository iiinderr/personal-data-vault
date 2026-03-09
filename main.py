from models.database import Base, engine, SessionLocal
from models.database import User, EncryptedNote, DocumentMetadata, UserRole , PasswordHint , AuditLog , init_db

# function called to create tables 
init_db()

print("Tables created successfully")

# create database session
db = SessionLocal()


# create a user
user = User(
    username="gaggi3",
    email="gaggi3@test.com",
    password_hash="hashedpassword123",
    role=UserRole.ADMIN
)

db.add(user)
db.commit()

print("User inserted")


# create encrypted note
note = EncryptedNote(
    title="My secret note",
    encrypted_content="encrypted_text_here",
    encryption_key_hint="family-key",
    user_id=user.id
)

db.add(note)
db.commit()

print("Encrypted note inserted")


# create document metadata
doc = DocumentMetadata(
    file_name="passport.pdf",
    file_type="application/pdf",
    file_size=300000,
    encrypted_file_path="encrypted/path/file123",
    tags="passport,personal",
    user_id=user.id
)

db.add(doc)
db.commit()

print("Document metadata inserted")

# create a passwordhint

hint = PasswordHint(
    service_name="Gmail",
    encrypted_hint="encrypted_hint_example",
    url="https://mail.google.com",
    user_id=user.id
)

db.add(hint)
db.commit()

print("Password hint inserted")

log = AuditLog(
    user_id=user.id,
    action="CREATE_NOTE",
    resource_type="encrypted_notes",
    resource_id=note.id,
    details="User created a note",
    ip_address="127.0.0.1"
)

db.add(log)
db.commit()

print("Audit log inserted")