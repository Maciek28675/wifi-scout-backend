from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.imports import Base
from app.routers import forum, users
from app.db import engine
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(forum.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI OK!"}