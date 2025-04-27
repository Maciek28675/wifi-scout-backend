from fastapi import APIRouter
from sqlalchemy import Engine, create_engine
from schemas import UserRegisterSchema
from crud import get_users, create_user
from models import Base

router = APIRouter(
    prefix="/user",
    tags=["User"],
)

DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)

@router.get("/users")
async def users():
    return get_users(engine)

@router.post("/register")
async def register(req: UserRegisterSchema):
    return create_user(engine, req)