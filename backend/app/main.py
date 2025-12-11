import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .cache import Cache
from .collector import Collector

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = Cache()

@app.on_event("startup")
async def start_services():
    await cache.connect()
    collector = Collector(cache)
    asyncio.create_task(collector.start())

@app.get("/metrics/latest")
async def latest_metrics():
    data = await cache.get_latest()
    if not data:
        raise HTTPException(404, "No metrics yet")
    return data
