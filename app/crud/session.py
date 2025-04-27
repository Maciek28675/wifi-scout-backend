from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.main import engine


def get_db_session(engine):
    return Session(engine)