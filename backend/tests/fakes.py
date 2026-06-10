"""In-memory adapters used to exercise use cases without a database/network."""
from datetime import datetime
from uuid import UUID

from src.domain.models import AdminUser, Entity, GatewayResult, PaymentStatus, Transaction


class FakeEntityRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, Entity] = {}

    async def add(self, entity: Entity) -> Entity:
        self._by_id[entity.id] = entity
        return entity

    async def get(self, entity_id: UUID) -> Entity | None:
        return self._by_id.get(entity_id)

    async def get_by_slug(self, slug: str) -> Entity | None:
        return next((e for e in self._by_id.values() if e.slug == slug), None)

    async def list(self) -> list[Entity]:
        return list(self._by_id.values())

    async def update(self, entity: Entity) -> Entity:
        self._by_id[entity.id] = entity
        return entity

    async def delete(self, entity_id: UUID) -> None:
        self._by_id.pop(entity_id, None)


class FakeTransactionRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, Transaction] = {}

    async def add(self, transaction: Transaction) -> Transaction:
        self._by_id[transaction.id] = transaction
        return transaction

    async def get(self, transaction_id: UUID) -> Transaction | None:
        return self._by_id.get(transaction_id)

    async def get_by_reference(self, reference: UUID) -> Transaction | None:
        return next((t for t in self._by_id.values() if t.reference == reference), None)

    async def update(self, transaction: Transaction) -> Transaction:
        self._by_id[transaction.id] = transaction
        return transaction

    async def search(
        self,
        *,
        entity_id: UUID | None = None,
        status: PaymentStatus | None = None,
        query: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        order: str = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Transaction], int]:
        items = list(self._by_id.values())
        if entity_id is not None:
            items = [t for t in items if t.entity_id == entity_id]
        if status is not None:
            items = [t for t in items if t.status is status]
        if query:
            q = query.strip().lower()
            items = [
                t
                for t in items
                if q
                in " ".join(
                    str(v).lower()
                    for v in (
                        t.customer_name,
                        t.customer_email,
                        t.customer_phone,
                        t.kkiapay_transaction_id,
                        t.reference,
                    )
                    if v
                )
            ]
        items.sort(key=lambda t: t.created_at, reverse=order != "asc")
        return items[offset : offset + limit], len(items)

    async def stats(self, entity_id: UUID | None = None) -> dict[str, int]:
        items = list(self._by_id.values())
        if entity_id is not None:
            items = [t for t in items if t.entity_id == entity_id]
        success = [t for t in items if t.status is PaymentStatus.SUCCESS]
        return {
            "total": len(items),
            "pending": sum(t.status is PaymentStatus.PENDING for t in items),
            "success": len(success),
            "failed": sum(t.status is PaymentStatus.FAILED for t in items),
            "success_amount": sum(t.amount for t in success),
        }

    async def daily_series(self, *, days: int = 14, entity_id: UUID | None = None) -> list[dict]:
        items = list(self._by_id.values())
        if entity_id is not None:
            items = [t for t in items if t.entity_id == entity_id]
        buckets: dict[str, dict] = {}
        for t in items:
            key = t.created_at.date().isoformat()
            b = buckets.setdefault(key, {"date": key, "count": 0, "success_amount": 0})
            b["count"] += 1
            if t.status is PaymentStatus.SUCCESS:
                b["success_amount"] += t.amount
        return [buckets[k] for k in sorted(buckets)]


class FakeAdminUserRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, AdminUser] = {}

    async def add(self, user: AdminUser) -> AdminUser:
        self._by_id[user.id] = user
        return user

    async def get(self, user_id: UUID) -> AdminUser | None:
        return self._by_id.get(user_id)

    async def get_by_email(self, email: str) -> AdminUser | None:
        return next((u for u in self._by_id.values() if u.email == email), None)

    async def list(self) -> list[AdminUser]:
        return list(self._by_id.values())

    async def update(self, user: AdminUser) -> AdminUser:
        self._by_id[user.id] = user
        return user

    async def delete(self, user_id: UUID) -> None:
        self._by_id.pop(user_id, None)


class FakeGateway:
    """Returns a preset status; records the ids it was asked to verify."""

    def __init__(self, status: PaymentStatus = PaymentStatus.SUCCESS, amount: int | None = None) -> None:
        self.status = status
        self.amount = amount
        self.calls: list[str] = []

    async def verify(self, transaction_id: str, *, entity: Entity) -> GatewayResult:
        self.calls.append(transaction_id)
        return GatewayResult(
            status=self.status, amount=self.amount, transaction_id=transaction_id, raw={"status": self.status.value}
        )


def make_entity(slug: str = "demo") -> Entity:
    return Entity(
        slug=slug,
        name="Demo",
        kkiapay_public_key="pub",
        kkiapay_private_key="priv",
        kkiapay_secret="sec",
        sandbox=True,
    )
