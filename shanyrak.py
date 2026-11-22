from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth import get_current_user
from database import (
    create_shanyrak, delete_shanyrak, get_all_shanyraks,
    get_shanyrak, update_shanyrak
)

router = APIRouter(prefix="/shanyraks", tags=["Shanyraks"])


class ShanyrakCreate(BaseModel):
    type: str = Field(min_length=1)
    price: int = Field(gt=0)
    address: str = Field(min_length=1)
    area: float = Field(gt=0)
    rooms_count: int = Field(gt=0)
    description: str = Field(min_length=1)


class ShanyrakUpdate(BaseModel):
    type: str | None = Field(default=None, min_length=1)
    price: int | None = Field(default=None, gt=0)
    address: str | None = Field(default=None, min_length=1)
    area: float | None = Field(default=None, gt=0)
    rooms_count: int | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, min_length=1)


def check_owner(shanyrak_id: int, user):
    existing = get_shanyrak(shanyrak_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if existing["user_id"] != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return existing


@router.post("/", status_code=200)
def create_listing(data: ShanyrakCreate, user=Depends(get_current_user)):
    shanyrak_id = create_shanyrak(user.user_id, data.model_dump())
    return {"id": shanyrak_id}


@router.get("/", status_code=200)
def list_listings():
    return get_all_shanyraks()


@router.get("/{shanyrak_id}", status_code=200)
def listing_details(shanyrak_id: int):
    existing = get_shanyrak(shanyrak_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {"id": existing["shanyrak_id"], **{
        key: value for key, value in existing.items() if key != "shanyrak_id"
    }}


@router.patch("/{shanyrak_id}", status_code=200)
def edit_listing(shanyrak_id: int, data: ShanyrakUpdate,
                 user=Depends(get_current_user)):
    check_owner(shanyrak_id, user)
    changes = data.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="No fields provided")
    if any(value is None for value in changes.values()):
        raise HTTPException(status_code=422, detail="Fields cannot be null")
    updated = update_shanyrak(shanyrak_id, changes)
    return {"id": updated["shanyrak_id"], **{
        key: value for key, value in updated.items() if key != "shanyrak_id"
    }}


@router.delete("/{shanyrak_id}", status_code=200)
def remove_listing(shanyrak_id: int, user=Depends(get_current_user)):
    check_owner(shanyrak_id, user)
    delete_shanyrak(shanyrak_id)
    return {"message": "Listing deleted"}
