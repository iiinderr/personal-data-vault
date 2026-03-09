from models.database import Base, engine

# create tables
Base.metadata.create_all(bind=engine)

print("Database created successfully")