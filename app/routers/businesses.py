from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Business, User
from ..schemas import BusinessIn, BusinessOut

router = APIRouter(prefix="/businesses", tags=["businesses"])


def _own_business(db: Session, user: User, business_id: int) -> Business:
    business = db.get(Business, business_id)
    if not business or business.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business not found"
        )
    return business


@router.get("", response_model=list[BusinessOut])
def list_my_businesses(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Business]:
    stmt = (
        select(Business)
        .where(Business.user_id == user.id)
        .order_by(Business.created_at.desc())
    )
    return list(db.scalars(stmt).all())


@router.post("", response_model=BusinessOut, status_code=status.HTTP_201_CREATED)
def create_business(
    data: BusinessIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Business:
    business = Business(user_id=user.id, **data.model_dump())
    db.add(business)
    db.commit()
    db.refresh(business)
    if user.active_business_id is None:
        user.active_business_id = business.id
        db.add(user)
        db.commit()
    return business


@router.get("/{business_id}", response_model=BusinessOut)
def read_business(
    business_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Business:
    return _own_business(db, user, business_id)


@router.put("/{business_id}", response_model=BusinessOut)
def update_business(
    business_id: int,
    data: BusinessIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Business:
    business = _own_business(db, user, business_id)
    for field, value in data.model_dump().items():
        setattr(business, field, value)
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_business(
    business_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    business = _own_business(db, user, business_id)
    db.delete(business)
    if user.active_business_id == business_id:
        user.active_business_id = None
        db.add(user)
    db.commit()
