import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis

from src.api import auth, photos, comments, users
@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_host = os.getenv("REDIS_HOST", "localhost")
    r = redis.Redis(host=redis_host, port=6379, db=0, encoding="utf-8", decode_responses=True)
    #await FastAPILimiter.init(r)
    yield
    await r.close()
app = FastAPI(title="PhotoShare API", lifespan=lifespan)
origins = [
    "http://localhost:3000",  
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)
app.include_router(auth.router, prefix="/api")
app.include_router(photos.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(users.router, prefix="/api")