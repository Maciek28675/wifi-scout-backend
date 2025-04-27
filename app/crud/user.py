import logging
from fastapi import HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import Engine
import bcrypt

from models import User
from schemas import UserRegisterSchema, UserLoginSchema
from auth.auth_handler import sign_jwt

# TODO: Zamienić na klase User
def get_users(engine: Engine):
    with Session(engine) as session:
        users = session.query(User).all()
        return users


def create_user(engine: Engine, req: UserRegisterSchema):
    with Session(engine) as session:
        if session.query(User).filter_by(email=req.email).first():
            logging.warning(f"Registration aborted – email already exists: {req.email}")
            raise HTTPException(status_code=400, detail="User already exists")
        
        if len(req.password) < 8:
            logging.warning("Registration aborted – password too short")
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(req.password.encode('utf-8'), salt).decode('utf-8')

        try:
            new_user = User(email=req.email, password=hashed_password)
            session.add(new_user)
            session.commit()
            logging.info(f"New user registered: {req.email}")
            return {"msg": "User registered successfully"}
        except Exception as e:
            session.rollback()
            logging.error(f"Error during registration for user {req.email}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during registration")


def login_user(engine: Engine, user: UserLoginSchema = Body(...)):
    with Session(engine) as session:
        try:
            db_user = session.query(User).filter_by(email=user.email).first()

            if not db_user:
                logging.warning(f"Login failed user not found: {user.email}")
                raise HTTPException(status_code=404, detail="User not found")
            
            if bcrypt.checkpw(user.password.encode('utf-8'), db_user.password.encode('utf-8')):
                logging.info(f"User logged in: {user.email}")
                return sign_jwt(db_user.email)
            else:
                logging.warning(f"Login failed incorrect password: {user.email}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
        except Exception as e:
            logging.error(f"Error during login for user {user.email}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during login")