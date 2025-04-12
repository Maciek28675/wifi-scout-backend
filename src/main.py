from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from init_db import Base, User, Measurement, Post
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

@app.get("/users")
async def get_users():
    with Session(engine) as session:
        users = session.query(User).all()
        return users

@app.post("/register")
async def create_user(email: str, password: str):
    with Session(engine) as session:
        new_user = User(email=email, password=password)
        session.add(new_user)
        session.commit()
        return new_user

@app.get("/login")
async def login(email: str, password: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(email=email, password=password).first()
        if user:
            return {"message": "Login successful", "user_id": user.user_id}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")