from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth import get_current_user
from database import (
    create_comment, delete_comment, get_comment, get_comments,
    get_shanyrak, update_comment
)

router = APIRouter(prefix="/shanyraks", tags=["Comments"])


class CommentCreate(BaseModel):
    content: str = Field(min_length=1)


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1)


def check_comment_owner(shanyrak_id: int, comment_id: int, user):
    comment = get_comment(shanyrak_id, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment["author_id"] != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return comment


@router.post("/{shanyrak_id}/comments", status_code=200)
def add_comment(shanyrak_id: int, data: CommentCreate,
                user=Depends(get_current_user)):
    if get_shanyrak(shanyrak_id) is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    comment_id = create_comment(shanyrak_id, user.user_id, data.content)
    return {"id": comment_id}


@router.get("/{shanyrak_id}/comments", status_code=200)
def listing_comments(shanyrak_id: int):
    if get_shanyrak(shanyrak_id) is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {"comments": get_comments(shanyrak_id)}


@router.patch("/{shanyrak_id}/comments/{comment_id}", status_code=200)
def edit_comment(shanyrak_id: int, comment_id: int, data: CommentUpdate,
                 user=Depends(get_current_user)):
    check_comment_owner(shanyrak_id, comment_id, user)
    update_comment(shanyrak_id, comment_id, data.content)
    return {"message": "Comment updated"}


@router.delete("/{shanyrak_id}/comments/{comment_id}", status_code=200)
def remove_comment(shanyrak_id: int, comment_id: int,
                   user=Depends(get_current_user)):
    check_comment_owner(shanyrak_id, comment_id, user)
    delete_comment(shanyrak_id, comment_id)
    return {"message": "Comment deleted"}