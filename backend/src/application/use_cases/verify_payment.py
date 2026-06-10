from uuid import UUID

from ...domain.exceptions import EntityNotFound, TransactionNotFound
from ...domain.models import PaymentStatus, Transaction
from ...domain.ports import EntityRepository, PaymentGateway, TransactionRepository


class VerifyPayment:
    """
    Confirm a transaction's real status with the gateway and persist it.

    Idempotent: once a transaction is SUCCESS/FAILED it is returned as-is unless
    `force` is set (used by the admin "re-verify" action).
    """

    def __init__(
        self,
        entities: EntityRepository,
        transactions: TransactionRepository,
        gateway: PaymentGateway,
    ) -> None:
        self._entities = entities
        self._transactions = transactions
        self._gateway = gateway

    async def by_reference(
        self, reference: UUID, *, kkiapay_transaction_id: str | None = None, force: bool = False
    ) -> Transaction:
        transaction = await self._transactions.get_by_reference(reference)
        if transaction is None:
            raise TransactionNotFound(f"Unknown reference '{reference}'.")
        return await self._verify(transaction, kkiapay_transaction_id, force)

    async def by_id(
        self, transaction_id: UUID, *, kkiapay_transaction_id: str | None = None, force: bool = True
    ) -> Transaction:
        transaction = await self._transactions.get(transaction_id)
        if transaction is None:
            raise TransactionNotFound(f"Unknown transaction '{transaction_id}'.")
        gateway_txn_id = kkiapay_transaction_id or transaction.kkiapay_transaction_id
        return await self._verify(transaction, gateway_txn_id, force)

    async def _verify(
        self, transaction: Transaction, kkiapay_transaction_id: str | None, force: bool
    ) -> Transaction:
        if transaction.status is not PaymentStatus.PENDING and not force:
            return transaction

        gateway_txn_id = kkiapay_transaction_id or transaction.kkiapay_transaction_id
        if not gateway_txn_id:
            return transaction

        entity = await self._entities.get(transaction.entity_id)
        if entity is None:
            raise EntityNotFound(str(transaction.entity_id))

        result = await self._gateway.verify(gateway_txn_id, entity=entity)
        transaction.mark(result.status, kkiapay_transaction_id=result.transaction_id or gateway_txn_id)
        if result.raw:
            transaction.metadata = {**transaction.metadata, "gateway": result.raw}
        return await self._transactions.update(transaction)
