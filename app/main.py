from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .routers import nginx, backup


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


@app.get("/")
def status():
    return {"status": "OK"}
