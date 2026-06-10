from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from .enums import PaymentStatus


@dataclass
class Transaction:
    """A payment attempt recorded locally, mirroring a Kkiapay transaction."""

    entity_id: UUID
    amount: int
    currency: str = "XOF"
    status: PaymentStatus = PaymentStatus.PENDING
    reference: UUID = field(default_factory=uuid4)
    kkiapay_transaction_id: str | None = None
    customer_name: str | None = None
    customer_email: str | None = None
    customer_phone: str | None = None
    metadata: dict = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def mark(self, status: PaymentStatus, kkiapay_transaction_id: str | None = None) -> None:
        self.status = status
        if kkiapay_transaction_id:
            self.kkiapay_transaction_id = kkiapay_transaction_id
        self.updated_at = datetime.utcnow()


@dataclass
class GatewayResult:
    """Outcome of verifying a transaction against the payment gateway."""

    status: PaymentStatus
    amount: int | None = None
    transaction_id: str | None = None
    raw: dict = field(default_factory=dict)
