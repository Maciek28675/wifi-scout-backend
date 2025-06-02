from fastapi import APIRouter
from app.schemas import UserRegisterSchema, UserLoginSchema
from app.crud import UserService
from fastapi import Depends, Body
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def users(db: Session = Depends(get_db)):
    service = UserService(db)
    return service.get_users(db)

@router.post("/register")
async def register(req: UserRegisterSchema, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.create_user(req)

@router.post("/login")
async def login(user: UserLoginSchema = Body(...), db: Session = Depends(get_db)):
    service = UserService(db)
    return service.login_user(user)