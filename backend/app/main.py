from fastapi import FastAPI
from app.db.database import database
from app.storage.minio_client import init_minio
from app.api.health import router as health_router
from app.api.test import router as test_router
from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.subject import router as subject_router
from app.api.import_data import router as import_router

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()
    init_minio()

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