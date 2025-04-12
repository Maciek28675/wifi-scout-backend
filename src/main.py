from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from init_db import Base, User, Measurement, Post
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from auth.auth_handler import sign_jwt
from model import UserRegisterSchema, UserLoginSchema
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    return {"message": "Hello from FastAPI OK!"}

@app.get("/users")
async def get_users():
    with Session(engine) as session:
        users = session.query(User).all()
        return users

@app.post("/user/register", tags=["user"])
async def create_user(req: UserRegisterSchema):
    with Session(engine) as session:
        hashed_password = pwd_context.hash(req.password)
        new_user = User(email=req.email, password=hashed_password)
        session.add(new_user)
        session.commit()
        return new_user
    
@app.post("/user/login", tags=["user"])
async def login_user(user: UserLoginSchema = Body(...)):
    with Session(engine) as session:
        db_user = session.query(User).filter_by(email=user.email).first()
        if db_user and pwd_context.verify(user.password, db_user.password):
            return sign_jwt(db_user.email)
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")