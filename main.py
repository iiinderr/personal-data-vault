
from fastapi import FastAPI

# Create app instance
app = FastAPI(
    title="Personal Data Vault",
    description="Privacy-first API with encryption and RBAC",
    version="1.0.0"
)


# Root endpoint
@app.get("/")
async def root():
    return {"message": "API is running"}