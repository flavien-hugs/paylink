from ...domain.exceptions import EntityNotFound, InvalidAmount
from ...domain.models import Transaction
from ...domain.ports import EntityRepository, TransactionRepository
from ..dto import InitiatePaymentCommand, InitiatePaymentResult


class InitiatePayment:
    """Create a PENDING transaction for an entity and return what the widget needs."""

    def __init__(self, entities: EntityRepository, transactions: TransactionRepository) -> None:
        self._entities = entities
        self._transactions = transactions

    async def execute(self, command: InitiatePaymentCommand) -> InitiatePaymentResult:
        if command.amount is None or command.amount <= 0:
            raise InvalidAmount("Amount must be a positive integer.")

        entity = await self._entities.get_by_slug(command.entity_slug)
        if entity is None or not entity.is_active:
            raise EntityNotFound(f"Unknown entity '{command.entity_slug}'.")

        transaction = Transaction(
            entity_id=entity.id,
            amount=command.amount,
            currency=entity.currency,
            customer_name=command.customer_name,
            customer_email=command.customer_email,
            customer_phone=command.customer_phone,
            metadata=command.metadata or {},
        )
        await self._transactions.add(transaction)

        return InitiatePaymentResult(
            reference=transaction.reference,
            amount=transaction.amount,
            currency=transaction.currency,
            public_key=entity.kkiapay_public_key,
            sandbox=entity.sandbox,
            entity_name=entity.name,
        )
