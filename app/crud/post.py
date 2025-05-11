import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, Engine

from app.models import Post, Vote, User
from app.schemas import PostCreate, VoteSchema

class PostService:
    def __init__(self, engine: Engine):
        self.engine = engine

    def create_post(self, post: PostCreate, current_user: User):
        with Session(self.engine) as session:
            try:
                new_post = Post(
                    user_id=current_user.user_id,
                    content=post.content,
                    location=post.location
                )
                session.add(new_post)
                session.commit()
                session.refresh(new_post)
                logging.info(f"New post created by user {current_user.email}")
                return {"msg": "Post created successfully"}
            except Exception as e:
                session.rollback()
                logging.error(f"Error creating post by user {current_user.email}: {e}")
                raise HTTPException(status_code=500, detail="Internal server error during post creation")

    def get_posts(self, sort: str, current_user: User):
        with Session(self.engine) as session:
            try:
                query = session.query(Post)

                if sort == "mine":
                    query = query.filter(Post.user_id == current_user.user_id)
                elif sort == "popular":
                    query = query.outerjoin(Vote).group_by(Post.post_id).order_by(func.sum(Vote.value).desc())
                else:
                    query = query.order_by(Post.created_at.desc())

                posts = query.all()
                results = []

                for post in posts:
                    upvotes = session.query(func.count(Vote.id)).filter(Vote.post_id == post.post_id, Vote.value == 1).scalar()
                    downvotes = session.query(func.count(Vote.id)).filter(Vote.post_id == post.post_id, Vote.value == -1).scalar()

                    user = session.query(User).filter(User.user_id == post.user_id).first()
                    initials = user.email.split("@")[0][:2] if user else "00"

                    results.append({
                        "post_id": post.post_id,
                        "user_id": post.user_id,
                        "content": post.content,
                        "location": post.location,
                        "created_at": post.created_at,
                        "upvotes": upvotes,
                        "downvotes": downvotes,
                        "user_initials": initials
                    })

                return results
            except Exception as e:
                logging.error(f"Error fetching posts: {e}")
                raise HTTPException(status_code=500, detail="Internal server error during posts fetching")

    def vote_on_post(self, vote: VoteSchema, current_user: User):
        with Session(self.engine) as session:
            try:
                post = session.query(Post).filter(Post.post_id == vote.post_id).first()
                if not post:
                    logging.warning(f"Vote failed - post not found: ID {vote.post_id}")
                    raise HTTPException(status_code=404, detail="Post not found")

                existing_vote = session.query(Vote).filter(
                    Vote.post_id == vote.post_id,
                    Vote.user_id == current_user.user_id
                ).first()

                if existing_vote:
                    if existing_vote.value == vote.value:
                        logging.warning(f"User {current_user.email} tried to vote the same way again on post {vote.post_id}")
                        raise HTTPException(status_code=400, detail="You have already voted this way")
                    
                    existing_vote.value = vote.value
                    session.commit()
                    logging.info(f"User {current_user.email} changed vote on post {vote.post_id}")
                    return {"msg": "Vote updated successfully"}
                else:
                    new_vote = Vote(
                        post_id=vote.post_id,
                        user_id=current_user.user_id,
                        value=vote.value
                    )
                    session.add(new_vote)
                    session.commit()
                    logging.info(f"User {current_user.email} voted on post {vote.post_id}")
                    return {"msg": "Vote added successfully"}

            except HTTPException:
                raise
            except Exception as e:
                session.rollback()
                logging.error(f"Error voting on post {vote.post_id} by user {current_user.email}: {e}")
                raise HTTPException(status_code=500, detail="Internal server error during voting")
