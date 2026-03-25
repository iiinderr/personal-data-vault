
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 

app = FastAPI(
    title="Personal Data Vault",
    description="Privacy-first API with encryption and RBAC",
    version="1.0.0"
)

# ✅ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # allow all (for development)
    allow_credentials=True,
    allow_methods=["*"],        # GET, POST, PUT, DELETE
    allow_headers=["*"],        # Authorization, Content-Type
)

@app.get("/")
async def root():
    return {"message": "API is running"}