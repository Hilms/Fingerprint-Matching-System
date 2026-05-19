import os
from fastapi import FastAPI
from databases import Database
from minio import Minio
from minio.error import S3Error

# ---------------------------
# ENV VARIABLES
# ---------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "fingerprints")

# ---------------------------
# APP INIT
# ---------------------------
app = FastAPI()

# ---------------------------
# DATABASE
# ---------------------------
database = Database(DATABASE_URL)

# ---------------------------
# MINIO CLIENT
# ---------------------------
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# ---------------------------
# STARTUP EVENT
# ---------------------------
@app.on_event("startup")
async def startup():
    # DB CONNECT
    await database.connect()
    print("Database connected")

    # MINIO SETUP
    try:
        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)
            print(f"Bucket '{MINIO_BUCKET}' created")
        else:
            print(f"Bucket '{MINIO_BUCKET}' already exists")

    except S3Error as e:
        print("MinIO error:", e)


# ---------------------------
# SHUTDOWN EVENT
# ---------------------------
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    print("Database disconnected")


# ---------------------------
# TEST ROUTES
# ---------------------------
@app.get("/")
def root():
    return {"status": "backend running"}


@app.get("/test-db")
async def test_db():
    query = "SELECT 1 as ok"
    result = await database.fetch_one(query)
    return {"db": result}


@app.get("/test-minio")
def test_minio():
    buckets = minio_client.list_buckets()
    return {"buckets": [b.name for b in buckets]}