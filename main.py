# main.py

from dotenv import load_dotenv

from fastapi import FastAPI
from routes.users import router as users_router
from routes.notes import router as notes_router
from routes.documents import router as documents_router
from routes.hints import router as hints_router
from routes.admin import router as admin_router

load_dotenv()
app = FastAPI()

# Mount routes
app.include_router(users_router, prefix="/api/v1/users")

app.include_router(notes_router, prefix="/notes")

app.include_router(documents_router, prefix="/documents")

app.include_router(hints_router, prefix="/hints")

app.include_router(admin_router, prefix="/admin")

@app.get("/")
def home():
    return {"message": "API is running"}