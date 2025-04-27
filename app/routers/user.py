from fastapi import APIRouter
from app.schemas import UserRegisterSchema, UserLoginSchema
from app.crud import get_users, create_user, login_user
from fastapi import Depends, Body
from sqlalchemy.orm import Session
from app.db import get_db

router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def users(db: Session = Depends(get_db)):
    return get_users(db)

@router.post("/register")
async def register(req: UserRegisterSchema, db: Session = Depends(get_db)):
    return create_user(db, req)

@router.post("/login")
async def login(user: UserLoginSchema = Body(...), db: Session = Depends(get_db)):
    return login_user(db, user)