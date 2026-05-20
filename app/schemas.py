from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------- Auth ----------


class SignupIn(BaseModel):
    """Create a new company account.

  Company fields are optional when signing up from the quote flow;
  they can be completed on the quote form afterward.
    """

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    contact_name: str | None = None
    phone: str | None = None

    company_name: str | None = Field(default=None, min_length=1, max_length=255)
    industry: str | None = None
    employee_count: str | None = None
    yearly_revenue: str | None = None
    website: str | None = None
    business_phone: str | None = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_new: bool = False


# ---------- User / company ----------


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr

    contact_name: str | None
    phone: str | None
    avatar_url: str | None
    theme: str

    company_name: str
    industry: str | None
    employee_count: str | None
    yearly_revenue: str | None
    website: str | None
    business_phone: str | None
    address_line1: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    country: str | None
    notes: str | None

    created_at: datetime
    has_password: bool = False


class UserUpdateIn(BaseModel):
    contact_name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    theme: Literal["light", "dark"] | None = None

    company_name: str | None = Field(default=None, min_length=1, max_length=255)
    industry: str | None = None
    employee_count: str | None = None
    yearly_revenue: str | None = None
    website: str | None = None
    business_phone: str | None = None
    address_line1: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    notes: str | None = None


class PasswordChangeIn(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# ---------- Quote ----------


class QuoteIn(BaseModel):
    service_slug: str = Field(min_length=1, max_length=80)
    service_name: str = Field(min_length=1, max_length=160)

    contact_name: str = Field(min_length=1, max_length=160)
    contact_email: EmailStr
    contact_phone: str | None = None

    company_name: str = Field(min_length=1, max_length=255)
    industry: str | None = None
    employee_count: str | None = None
    yearly_revenue: str | None = None

    monthly_budget: str | None = None
    timeline: str | None = None
    goals: str | None = None
    notes: str | None = None
    referral_source: str | None = None


class QuoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int

    service_slug: str
    service_name: str

    contact_name: str
    contact_email: EmailStr
    contact_phone: str | None

    company_name: str
    industry: str | None
    employee_count: str | None
    yearly_revenue: str | None

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


class AnalyticsPoint(BaseModel):
    label: str
    spent: float
    returned: float


class AnalyticsOut(BaseModel):
    total_spent: float
    total_returned: float
    roas: float
    active_campaigns: int
    leads_this_month: int
    impressions: int
    clicks: int
    conversions: int
    history: list[AnalyticsPoint]
