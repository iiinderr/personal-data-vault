# main.py

from fastapi import FastAPI
from routes.users import router as user_router

app = FastAPI()

# Mount routes
app.include_router(user_router, prefix="/api/v1/users")

@app.get("/")
def home():
    return {"message": "API is running"}