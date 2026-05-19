from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Business, User
from ..schemas import UserOut, UserUpdateIn

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def read_me(user: User = Depends(get_current_user)) -> User:
    return user


@router.put("/me", response_model=UserOut)
def update_me(
    data: UserUpdateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    updates = data.model_dump(exclude_unset=True)

    if "active_business_id" in updates and updates["active_business_id"] is not None:
        biz = db.get(Business, updates["active_business_id"])
        if not biz or biz.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Active business must belong to you",
            )

    for field, value in updates.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
