from typing import Protocol

from ..models import Entity, GatewayResult


class PaymentGateway(Protocol):
    """Port to the external payment aggregator (Kkiapay)."""

    async def verify(self, transaction_id: str, *, entity: Entity) -> GatewayResult:
        """Verify a transaction server-side and return its authoritative status."""
        ...
