from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import String, case, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.models import AdminUser, Entity, PaymentStatus, Transaction
from ..security import FernetCipher
from . import mappers
from .orm import AdminUserRow, EntityRow, TransactionRow


class PgEntityRepository:
    def __init__(self, session: AsyncSession, cipher: FernetCipher) -> None:
        self._session = session
        self._cipher = cipher

    async def add(self, entity: Entity) -> Entity:
        row = EntityRow(id=entity.id, created_at=entity.created_at)
        mappers.apply_entity_to_row(entity, row, self._cipher)
        self._session.add(row)
        await self._session.flush()
        return entity

    async def get(self, entity_id: UUID) -> Entity | None:
        row = await self._session.get(EntityRow, entity_id)
        return mappers.entity_to_domain(row, self._cipher) if row else None

    async def get_by_slug(self, slug: str) -> Entity | None:
        result = await self._session.execute(select(EntityRow).where(EntityRow.slug == slug))
        row = result.scalar_one_or_none()
        return mappers.entity_to_domain(row, self._cipher) if row else None

    async def list(self) -> list[Entity]:
        result = await self._session.execute(select(EntityRow).order_by(EntityRow.created_at.desc()))
        return [mappers.entity_to_domain(row, self._cipher) for row in result.scalars()]

    async def update(self, entity: Entity) -> Entity:
        row = await self._session.get(EntityRow, entity.id)
        if row is None:
            raise ValueError(f"Entity {entity.id} not found")
        mappers.apply_entity_to_row(entity, row, self._cipher)
        await self._session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> None:
        row = await self._session.get(EntityRow, entity_id)
        if row is not None:
            await self._session.delete(row)
            await self._session.flush()


class PgTransactionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, transaction: Transaction) -> Transaction:
        row = TransactionRow(id=transaction.id, created_at=transaction.created_at)
        mappers.apply_transaction_to_row(transaction, row)
        self._session.add(row)
        await self._session.flush()
        return transaction

    async def get(self, transaction_id: UUID) -> Transaction | None:
        row = await self._session.get(TransactionRow, transaction_id)
        return mappers.transaction_to_domain(row) if row else None

    async def get_by_reference(self, reference: UUID) -> Transaction | None:
        result = await self._session.execute(
            select(TransactionRow).where(TransactionRow.reference == reference)
        )
        row = result.scalar_one_or_none()
        return mappers.transaction_to_domain(row) if row else None

    async def update(self, transaction: Transaction) -> Transaction:
        row = await self._session.get(TransactionRow, transaction.id)
        if row is None:
            raise ValueError(f"Transaction {transaction.id} not found")
        mappers.apply_transaction_to_row(transaction, row)
        await self._session.flush()
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
        filters = []
        if entity_id is not None:
            filters.append(TransactionRow.entity_id == entity_id)
        if status is not None:
            filters.append(TransactionRow.status == status.value)
        if query:
            like = f"%{query.strip()}%"
            filters.append(
                or_(
                    TransactionRow.customer_name.ilike(like),
                    TransactionRow.customer_email.ilike(like),
                    TransactionRow.customer_phone.ilike(like),
                    TransactionRow.kkiapay_transaction_id.ilike(like),
                    cast(TransactionRow.reference, String).ilike(like),
                )
            )
        if date_from is not None:
            filters.append(TransactionRow.created_at >= date_from)
        if date_to is not None:
            filters.append(TransactionRow.created_at <= date_to)

        base = select(TransactionRow).where(*filters)
        total = await self._session.scalar(
            select(func.count()).select_from(base.subquery())
        )
        ordering = (
            TransactionRow.created_at.asc()
            if order == "asc"
            else TransactionRow.created_at.desc()
        )
        result = await self._session.execute(
            base.order_by(ordering).limit(limit).offset(offset)
        )
        items = [mappers.transaction_to_domain(row) for row in result.scalars()]
        return items, int(total or 0)

    async def stats(self, entity_id: UUID | None = None) -> dict[str, int]:
        filters = [TransactionRow.entity_id == entity_id] if entity_id else []
        result = await self._session.execute(
            select(TransactionRow.status, func.count(), func.coalesce(func.sum(TransactionRow.amount), 0))
            .where(*filters)
            .group_by(TransactionRow.status)
        )
        counts = {status.value: 0 for status in PaymentStatus}
        total_count = 0
        success_amount = 0
        for status, count, amount in result.all():
            counts[status] = int(count)
            total_count += int(count)
            if status == PaymentStatus.SUCCESS.value:
                success_amount = int(amount)
        return {
            "total": total_count,
            "pending": counts[PaymentStatus.PENDING.value],
            "success": counts[PaymentStatus.SUCCESS.value],
            "failed": counts[PaymentStatus.FAILED.value],
            "success_amount": success_amount,
        }

    async def daily_series(self, *, days: int = 14, entity_id: UUID | None = None) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days - 1)
        day = func.date(TransactionRow.created_at)
        success_amount = func.coalesce(
            func.sum(case((TransactionRow.status == PaymentStatus.SUCCESS.value, TransactionRow.amount), else_=0)),
            0,
        )
        filters = [TransactionRow.created_at >= cutoff]
        if entity_id is not None:
            filters.append(TransactionRow.entity_id == entity_id)
        result = await self._session.execute(
            select(day.label("d"), func.count(), success_amount).where(*filters).group_by(day).order_by(day)
        )
        return [
            {"date": str(d), "count": int(count), "success_amount": int(amount)}
            for d, count, amount in result.all()
        ]


class PgAdminUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user: AdminUser) -> AdminUser:
        row = AdminUserRow(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_superadmin=user.is_superadmin,
            created_at=user.created_at,
        )
        self._session.add(row)
        await self._session.flush()
        return user

    async def get(self, user_id: UUID) -> AdminUser | None:
        row = await self._session.get(AdminUserRow, user_id)
        return mappers.admin_to_domain(row) if row else None

    async def get_by_email(self, email: str) -> AdminUser | None:
        result = await self._session.execute(select(AdminUserRow).where(AdminUserRow.email == email))
        row = result.scalar_one_or_none()
        return mappers.admin_to_domain(row) if row else None

    async def list(self) -> list[AdminUser]:
        result = await self._session.execute(select(AdminUserRow).order_by(AdminUserRow.created_at.desc()))
        return [mappers.admin_to_domain(row) for row in result.scalars()]

    async def update(self, user: AdminUser) -> AdminUser:
        row = await self._session.get(AdminUserRow, user.id)
        if row is None:
            raise ValueError(f"Admin user {user.id} not found")
        row.email = user.email
        row.hashed_password = user.hashed_password
        row.is_active = user.is_active
        row.is_superadmin = user.is_superadmin
        await self._session.flush()
        return user

    async def delete(self, user_id: UUID) -> None:
        row = await self._session.get(AdminUserRow, user_id)
        if row is not None:
            await self._session.delete(row)
            await self._session.flush()
