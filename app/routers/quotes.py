from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import QuoteRequest, User
from ..schemas import QuoteIn, QuoteOut
from ..services_catalog import get_service

router = APIRouter(prefix="/quotes", tags=["quotes"])


def _get_user_quote(db: Session, user_id: int) -> QuoteRequest | None:
    return db.scalar(
        select(QuoteRequest)
        .where(QuoteRequest.user_id == user_id)
        .order_by(QuoteRequest.created_at.desc())
        .limit(1)
    )


@router.get("", response_model=list[QuoteOut])
def list_my_quotes(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[QuoteRequest]:
    quote = _get_user_quote(db, user.id)
    return [quote] if quote else []


@router.post("", response_model=QuoteOut, status_code=status.HTTP_201_CREATED)
def create_quote(
    data: QuoteIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuoteRequest:
    if _get_user_quote(db, user.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have a quote request. Edit your existing quote instead.",
        )

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


@router.put("/{quote_id}", response_model=QuoteOut)
def update_quote(
    quote_id: int,
    data: QuoteIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuoteRequest:
    quote = db.get(QuoteRequest, quote_id)
    if not quote or quote.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found"
        )

    service = get_service(data.service_slug)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown service slug",
        )

    for field, value in data.model_dump().items():
        setattr(quote, field, value)

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
