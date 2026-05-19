from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# Users and Businesses reference each other (users.active_business_id ↔
# businesses.user_id). Mark the user→business FK with use_alter=True so
# SQLAlchemy knows the cycle is intentional and DDL ordering works.


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )
    apple_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )

    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    theme: Mapped[str] = mapped_column(String(16), default="dark")

    active_business_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "businesses.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_users_active_business",
        ),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    businesses: Mapped[list["Business"]] = relationship(
        "Business",
        back_populates="owner",
        cascade="all, delete-orphan",
        foreign_keys="Business.user_id",
    )
    quotes: Mapped[list["QuoteRequest"]] = relationship(
        "QuoteRequest", back_populates="user", cascade="all, delete-orphan"
    )


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    name: Mapped[str] = mapped_column(String(255))
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    size: Mapped[str | None] = mapped_column(String(60), nullable=True)
    employee_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    yearly_revenue: Mapped[float | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )

    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(40), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    owner: Mapped[User] = relationship(
        "User", back_populates="businesses", foreign_keys=[user_id]
    )
    quotes: Mapped[list["QuoteRequest"]] = relationship(
        "QuoteRequest", back_populates="business", cascade="all, delete-orphan"
    )


class QuoteRequest(Base):
    __tablename__ = "quote_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    business_id: Mapped[int | None] = mapped_column(
        ForeignKey("businesses.id", ondelete="SET NULL"), nullable=True, index=True
    )

    service_slug: Mapped[str] = mapped_column(String(80), index=True)
    service_name: Mapped[str] = mapped_column(String(160))

    contact_name: Mapped[str] = mapped_column(String(160))
    contact_email: Mapped[str] = mapped_column(String(255))
    contact_phone: Mapped[str | None] = mapped_column(String(40), nullable=True)

    business_name: Mapped[str] = mapped_column(String(255))
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    business_size: Mapped[str | None] = mapped_column(String(60), nullable=True)
    employee_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    yearly_revenue: Mapped[float | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )

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
    business: Mapped[Business | None] = relationship(
        "Business", back_populates="quotes"
    )
