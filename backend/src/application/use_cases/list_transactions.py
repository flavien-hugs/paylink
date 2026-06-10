from datetime import datetime
from uuid import UUID

from ...domain.exceptions import TransactionNotFound
from ...domain.models import PaymentStatus, Transaction
from ...domain.ports import TransactionRepository


class ListTransactions:
    def __init__(self, transactions: TransactionRepository) -> None:
        self._transactions = transactions

    async def execute(
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
        return await self._transactions.search(
            entity_id=entity_id,
            status=status,
            query=query,
            date_from=date_from,
            date_to=date_to,
            order=order,
            limit=limit,
            offset=offset,
        )


class GetTransaction:
    def __init__(self, transactions: TransactionRepository) -> None:
        self._transactions = transactions

    async def execute(self, transaction_id: UUID) -> Transaction:
        transaction = await self._transactions.get(transaction_id)
        if transaction is None:
            raise TransactionNotFound(str(transaction_id))
        return transaction


class TransactionStats:
    def __init__(self, transactions: TransactionRepository) -> None:
        self._transactions = transactions

    async def execute(self, *, entity_id: UUID | None = None) -> dict[str, int]:
        return await self._transactions.stats(entity_id=entity_id)
