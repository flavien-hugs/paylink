from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from ...domain.models import PaymentStatus


# ----- Public / payment flow -----
class PublicEntityOut(BaseModel):
    slug: str
    name: str
    description: str | None
    logo_url: str | None
    primary_color: str
    secondary_color: str
    currency: str
    public_key: str
    sandbox: bool


class InitiatePaymentIn(BaseModel):
    amount: int = Field(gt=0, description="Amount in the entity currency's minor-less unit (e.g. XOF).")
    customer_name: str | None = None
    customer_email: EmailStr | None = None
    customer_phone: str | None = None
    metadata: dict | None = None


class InitiatePaymentOut(BaseModel):
    reference: UUID
    amount: int
    currency: str
    public_key: str
    sandbox: bool
    entity_name: str


class VerifyPaymentIn(BaseModel):
    kkiapay_transaction_id: str


class ReverifyIn(BaseModel):
    # Optional: lets an admin reconcile an orphan PENDING transaction by supplying
    # the Kkiapay transaction id manually. Falls back to the stored id if omitted.
    kkiapay_transaction_id: str | None = None


# ----- Transactions -----
class TransactionOut(BaseModel):
    id: UUID
    reference: UUID
    kkiapay_transaction_id: str | None
    entity_id: UUID
    amount: int
    currency: str
    status: PaymentStatus
    customer_name: str | None
    customer_email: str | None
    customer_phone: str | None
    metadata: dict
    created_at: datetime
    updated_at: datetime


class PaginatedTransactions(BaseModel):
    items: list[TransactionOut]
    total: int
    limit: int
    offset: int


class StatsOut(BaseModel):
    total: int
    pending: int
    success: int
    failed: int
    success_amount: int


class EntityStatOut(BaseModel):
    entity_id: UUID
    name: str
    total: int
    success: int
    pending: int
    failed: int
    success_amount: int


class DailyPointOut(BaseModel):
    date: str
    count: int
    success_amount: int


class StatsReportOut(BaseModel):
    overall: StatsOut
    by_entity: list[EntityStatOut]
    daily: list[DailyPointOut]


# ----- Admin users -----
class AdminUserOut(BaseModel):
    id: UUID
    email: str
    is_active: bool
    is_superadmin: bool
    created_at: datetime


class AdminUserIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    is_active: bool = True


class AdminUserUpdateIn(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6)
    is_active: bool | None = None


class ChangePasswordIn(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)


# ----- Admin auth -----
class LoginIn(BaseModel):
    # Plain str (not EmailStr): the login is an identifier, so we must not run
    # deliverability checks that reject reserved TLDs like `.local`.
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ----- Entities (admin) -----
class EntityIn(BaseModel):
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,62}$")
    name: str
    description: str | None = None
    kkiapay_public_key: str
    kkiapay_private_key: str
    kkiapay_secret: str
    logo_url: str | None = None
    primary_color: str = "#2563eb"
    secondary_color: str = "#1e293b"
    currency: str = "XOF"
    sandbox: bool = True
    success_url: str | None = None
    failure_url: str | None = None
    is_active: bool = True


class EntityUpdateIn(BaseModel):
    slug: str | None = Field(default=None, pattern=r"^[a-z0-9][a-z0-9-]{1,62}$")
    name: str | None = None
    description: str | None = None
    kkiapay_public_key: str | None = None
    kkiapay_private_key: str | None = None
    kkiapay_secret: str | None = None
    logo_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    currency: str | None = None
    sandbox: bool | None = None
    success_url: str | None = None
    failure_url: str | None = None
    is_active: bool | None = None


class EntityOut(BaseModel):
    """Admin view — exposes credentials (back-office only, behind JWT)."""

    id: UUID
    slug: str
    name: str
    description: str | None
    logo_url: str | None
    primary_color: str
    secondary_color: str
    currency: str
    kkiapay_public_key: str
    kkiapay_private_key: str
    kkiapay_secret: str
    sandbox: bool
    success_url: str | None
    failure_url: str | None
    is_active: bool
    created_at: datetime
