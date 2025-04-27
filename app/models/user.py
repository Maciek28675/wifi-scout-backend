from .imports import *

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    signUpDate = Column(Date, default=datetime.now().date())