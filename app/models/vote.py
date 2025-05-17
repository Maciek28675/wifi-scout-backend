from .imports import *

class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    value = Column(Integer, default=1)  # tylko upvote

    __table_args__ = (UniqueConstraint('post_id', 'user_id', name='unique_vote'),)
