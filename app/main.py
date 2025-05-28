from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base
from app.routers.user import router as user_router
from app.db.database import engine
from app.routers.measurements import router as measurements_router
import logging
from app.models.user import User
from app.models.measurement import Measurement



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
app.include_router(user_router)
app.include_router(measurements_router)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI OK!"}