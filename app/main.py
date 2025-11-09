from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

from .routers import nginx, backup
from .utils.environment import OUTPUT_DIR


logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(nginx.router, prefix="/nginx", tags=["nginx"])
app.include_router(backup.router, prefix="/backup", tags=["backup"])
app.mount("/static", StaticFiles(directory=OUTPUT_DIR), name="static")


@app.get("/")
def status():
    return {"status": "OK"}
