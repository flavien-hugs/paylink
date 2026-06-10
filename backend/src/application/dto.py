from dataclasses import dataclass
from uuid import UUID


@dataclass
class InitiatePaymentCommand:
    entity_slug: str
    amount: int
    customer_name: str | None = None
    customer_email: str | None = None
    customer_phone: str | None = None
    metadata: dict | None = None


@dataclass
class InitiatePaymentResult:
    reference: UUID
    amount: int
    currency: str
    public_key: str
    sandbox: bool
    entity_name: str


@dataclass
class PublicEntityView:
    """Branding-only projection of an entity, safe to expose publicly."""

    slug: str
    name: str
    description: str | None
    logo_url: str | None
    primary_color: str
    secondary_color: str
    currency: str
    public_key: str
    sandbox: bool
