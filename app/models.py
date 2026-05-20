from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    """A DigiPros account.

    Accounts are company-based, not person-based — one company = one
    account. The email + password (or OAuth identity) belongs to the
    person who manages the account, but the account itself represents
    the company.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )
    apple_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )

    # Person managing the account
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    theme: Mapped[str] = mapped_column(String(16), default="dark")

    # Company / business identity (the account IS the company)
    company_name: Mapped[str] = mapped_column(String(255), index=True)
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    employee_count: Mapped[str | None] = mapped_column(String(60), nullable=True)
    yearly_revenue: Mapped[str | None] = mapped_column(String(60), nullable=True)

    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    business_phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(40), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    quotes: Mapped[list["QuoteRequest"]] = relationship(
        "QuoteRequest", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def has_password(self) -> bool:
        return self.hashed_password is not None


class QuoteRequest(Base):
    __tablename__ = "quote_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    # We store a snapshot of the requested services + business state at
    # the time of submission so the quote stays meaningful even if the
    # account is later edited.
    service_slug: Mapped[str] = mapped_column(String(80), index=True)
    service_name: Mapped[str] = mapped_column(String(160))

    contact_name: Mapped[str] = mapped_column(String(160))
    contact_email: Mapped[str] = mapped_column(String(255))
    contact_phone: Mapped[str | None] = mapped_column(String(40), nullable=True)

    company_name: Mapped[str] = mapped_column(String(255))
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    employee_count: Mapped[str | None] = mapped_column(String(60), nullable=True)
    yearly_revenue: Mapped[str | None] = mapped_column(String(60), nullable=True)

    monthly_budget: Mapped[str | None] = mapped_column(String(60), nullable=True)
    timeline: Mapped[str | None] = mapped_column(String(60), nullable=True)
    goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    referral_source: Mapped[str | None] = mapped_column(String(120), nullable=True)

    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped[User] = relationship("User", back_populates="quotes")
