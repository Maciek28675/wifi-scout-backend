from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import declarative_base, Session
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)
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
    content = Column(String)
    location = Column(String)

engine = create_engine('sqlite:///database.db', echo=True)

Base.metadata.create_all(engine)

with Session(engine) as session:
    new_user = User(email="272488@student.pwr.edu.pl", password="password")
    session.add(new_user)
    session.commit()
