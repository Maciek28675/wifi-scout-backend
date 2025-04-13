from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import declarative_base, Session
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    signUpDate = Column(Date, default=datetime.now().date())

class Measurement(Base):
    __tablename__ = 'measurements'
    measurement_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    latitude = Column(Float)
    longitude = Column(Float)
    signalStrength = Column(Integer)
    downloadSpeed = Column(Float)
    uploadSpeed = Column(Float)
    ping = Column(Integer)

class Post(Base):
    __tablename__ = 'posts'
    post_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    content = Column(String(500)) # liczba znakow w poscie do ustalenia
    location = Column(String(50))