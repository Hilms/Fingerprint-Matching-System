from fastapi import APIRouter
from app.db.database import database
from app.storage.minio_client import minio_client

router = APIRouter()

@router.get("/test-db")
async def test_db():
    result = await database.fetch_one("SELECT 1 as ok")
    return {"db": result}

@router.get("/test-minio")
def test_minio():
    buckets = minio_client.list_buckets()
    return {"buckets": [b.name for b in buckets]}