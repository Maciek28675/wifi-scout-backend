from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class PostCreate(BaseModel):
    content: str = Field(..., max_length=4)
    location: Literal[
    "A-1", "A-2", "A-3", "A-4", "A-5", "A-6", "A-7", "A-8", "A-9", "A-10",
    "B-1", "B-2", "B-4", "B-5", "B-6", "B-7", "B-8", "B-9", "B-11",
    "C-1", "C-2", "C-3", "C-4", "C-5", "C-6", "C-7", "C-8", "C-11", "C-13", "C-14", "C-15", "C-16", "C-18", "C-19", "C-20",
    "D-1", "D-2", "D-3", "D-20", "D-21",
    "F-1", "F-2", "F-3", "F-4",
    "H-3", "H-4", "H-5", "H-6", "H-7", "H-8", "H-9", "H-10", "H-12", "H-13", "H-14",
    "L-1", "L-2", "L-3",
    ]

class PostOut(BaseModel):
    post_id: int
    user_id: int
    content: str
    location: str
    created_at: datetime
    upvotes: int
    user_initials: str

    class Config:
        orm_mode = True

class VoteSchema(BaseModel):
    post_id: int
