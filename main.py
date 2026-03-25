
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.users import router as users_router
from routes.notes import router as notes_router
from routes.documents import router as docs_router
from routes.hints import router as hints_router
from routes.admin import router as admin_router


app = FastAPI(
    title="Personal Data Vault",
    description="Privacy-first API with encryption and RBAC",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router,  prefix="/api/v1/users",     tags=["Users"])
app.include_router(notes_router,  prefix="/api/v1/notes",     tags=["Encrypted Notes"])
app.include_router(docs_router,   prefix="/api/v1/documents", tags=["Documents"])
app.include_router(hints_router,  prefix="/api/v1/hints",     tags=["Password Hints"])
app.include_router(admin_router,  prefix="/api/v1/admin",     tags=["Admin"])


@app.get("/health", tags=["Health"])
async def health_check():
    
    return {"status": "healthy", "service": "Personal Data Vault"}


@app.get("/")
async def root():
    return {"message": "API is running"}