from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import QuoteRequest, User
from ..schemas import QuoteIn, QuoteOut
from ..services_catalog import get_service

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.get("", response_model=list[QuoteOut])
def list_my_quotes(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[QuoteRequest]:
    stmt = (
        select(QuoteRequest)
        .where(QuoteRequest.user_id == user.id)
        .order_by(QuoteRequest.created_at.desc())
    )
    return list(db.scalars(stmt).all())


@router.post("", response_model=QuoteOut, status_code=status.HTTP_201_CREATED)
def create_quote(
    data: QuoteIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuoteRequest:
    service = get_service(data.service_slug)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown service slug",
        )

    quote = QuoteRequest(
        user_id=user.id,
        status="pending",
        **data.model_dump(),
    )
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote


@router.get("/{quote_id}", response_model=QuoteOut)
def read_quote(
    quote_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuoteRequest:
    quote = db.get(QuoteRequest, quote_id)
    if not quote or quote.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found"
        )
    return quote
