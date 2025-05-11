from .imports import *

class Post(Base):
    __tablename__ = 'posts'
    post_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    content = Column(String(500)) # liczba znakow w poscie do ustalenia
    location = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
