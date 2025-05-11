from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import PostCreate, VoteSchema
from app.crud.post import PostService
from app.db import get_db
from app.auth.auth_bearer import get_current_user
from app.models import User

router = APIRouter(
    prefix="/forum",
    tags=["Forum"],
    responses={404: {"description": "Not found"}},
)

@router.post("/post")
async def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post_service = PostService(db.bind)
    return post_service.create_post(post, current_user)

@router.get("/posts")
async def get_posts(
    sort: str = "latest",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post_service = PostService(db.bind)
    return post_service.get_posts(sort, current_user)

@router.post("/vote")
async def vote_on_post(
    vote: VoteSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post_service = PostService(db.bind)
    return post_service.vote_on_post(vote, current_user)
