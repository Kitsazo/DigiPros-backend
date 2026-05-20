from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import PasswordChangeIn, UserOut, UserUpdateIn
from ..security import hash_password, verify_password

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
    for field, value in updates.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: PasswordChangeIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password sign-in is not enabled for this account",
        )
    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    user.hashed_password = hash_password(data.new_password)
    db.add(user)
    db.commit()
