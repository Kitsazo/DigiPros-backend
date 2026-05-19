from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------- Auth ----------


class BusinessSignupInfo(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    industry: str | None = None
    size: str | None = None
    employee_count: int | None = Field(default=None, ge=0)
    yearly_revenue: float | None = Field(default=None, ge=0)
    website: str | None = None
    phone: str | None = None


class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str | None = None
    phone: str | None = None
    business: BusinessSignupInfo | None = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- User ----------


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str | None
    phone: str | None
    avatar_url: str | None
    theme: str
    active_business_id: int | None
    created_at: datetime


class UserUpdateIn(BaseModel):
    name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    theme: Literal["light", "dark"] | None = None
    active_business_id: int | None = None


# ---------- Business ----------


class BusinessIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    industry: str | None = None
    size: str | None = None
    employee_count: int | None = Field(default=None, ge=0)
    yearly_revenue: float | None = Field(default=None, ge=0)
    website: str | None = None
    phone: str | None = None
    address_line1: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    notes: str | None = None


class BusinessOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    industry: str | None
    size: str | None
    employee_count: int | None
    yearly_revenue: float | None
    website: str | None
    phone: str | None
    address_line1: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    country: str | None
    notes: str | None
    created_at: datetime


# ---------- Quote ----------


class QuoteIn(BaseModel):
    service_slug: str = Field(min_length=1, max_length=80)
    service_name: str = Field(min_length=1, max_length=160)

    contact_name: str = Field(min_length=1, max_length=160)
    contact_email: EmailStr
    contact_phone: str | None = None

    business_name: str = Field(min_length=1, max_length=255)
    industry: str | None = None
    business_size: str | None = None
    employee_count: int | None = Field(default=None, ge=0)
    yearly_revenue: float | None = Field(default=None, ge=0)

    monthly_budget: str | None = None
    timeline: str | None = None
    goals: str | None = None
    notes: str | None = None
    referral_source: str | None = None

    business_id: int | None = None


class QuoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    business_id: int | None

    service_slug: str
    service_name: str

    contact_name: str
    contact_email: EmailStr
    contact_phone: str | None

    business_name: str
    industry: str | None
    business_size: str | None
    employee_count: int | None
    yearly_revenue: float | None

    monthly_budget: str | None
    timeline: str | None
    goals: str | None
    notes: str | None
    referral_source: str | None

    status: str
    created_at: datetime


# ---------- Services / Analytics ----------


class ServiceOut(BaseModel):
    slug: str
    name: str
    tagline: str
    description: str
    starts_at: str
    deliverables: list[str]
    icon: str


class AnalyticsOut(BaseModel):
    total_spent: float
    total_returned: float
    roas: float
    active_campaigns: int
    leads_this_month: int
    impressions: int
    clicks: int
    conversions: int
    history: list["AnalyticsPoint"]


class AnalyticsPoint(BaseModel):
    label: str
    spent: float
    returned: float


AnalyticsOut.model_rebuild()
