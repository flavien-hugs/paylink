from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Entity:
    """
    A payable entity (e.g. a school, an association). Carries its own visual
    identity (logo, name, colors) and its own Kkiapay credentials, so that a
    single payment page codebase can be reused for many entities by slug.

    The Kkiapay secret credentials (`kkiapay_private_key`, `kkiapay_secret`) are
    stored encrypted at rest by the persistence adapter and must never be
    serialized to the public API.
    """

    slug: str
    name: str
    kkiapay_public_key: str
    kkiapay_private_key: str
    kkiapay_secret: str
    description: str | None = None
    logo_url: str | None = None
    primary_color: str = "#2563eb"
    secondary_color: str = "#1e293b"
    currency: str = "XOF"
    sandbox: bool = True
    success_url: str | None = None
    failure_url: str | None = None
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
