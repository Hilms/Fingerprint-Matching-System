from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.db.database import database
from app.jobs.dashboard_refresh import start_scheduler
from app.storage.minio_client import init_minio

from app.api.health import router as health_router
from app.api.test import router as test_router
from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.subject import router as subject_router
from app.api.import_data import router as import_router
from app.api.fingerprint import router as fingerprint_router
from app.api.dashboard import router as dashboard_router

from app.dependencies import user_service

app = FastAPI()

origins = [
    "http://localhost:" + os.getenv("FRONTEND_PORT")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()
    start_scheduler(database)
    init_minio()

    admin = await user_service.get_user("admin")
    if not admin:
        await user_service.create_admin({
            "first_name": "admin",
            "last_name": "admin",
            "username": "admin",
            "email": "admin@example.de",
            "password": os.getenv("ADMIN_PASSWORD"),
            "role" : "admin"
        })

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
def root():
    return {"status": "running"}

app.include_router(health_router)
app.include_router(test_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(subject_router)
app.include_router(import_router)
app.include_router(fingerprint_router)
app.include_router(dashboard_router)