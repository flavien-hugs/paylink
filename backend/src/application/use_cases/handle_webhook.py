from ...domain.exceptions import TransactionNotFound, WebhookVerificationError
from ...domain.models import Transaction
from ...domain.ports import TransactionRepository
from .verify_payment import VerifyPayment


class HandleKkiapayWebhook:
    """
    Process a Kkiapay webhook notification. The payload is untrusted, so we never
    trust its status directly: we extract the transaction id, locate the local
    transaction and re-verify server-side via the gateway (authoritative).
    """

    def __init__(self, transactions: TransactionRepository, verify_payment: VerifyPayment) -> None:
        self._transactions = transactions
        self._verify = verify_payment

    async def execute(self, payload: dict) -> Transaction:
        kkiapay_txn_id = payload.get("transactionId") or payload.get("transaction_id")
        if not kkiapay_txn_id:
            raise WebhookVerificationError("Missing transaction id in webhook payload.")

        # Kkiapay echoes our reference back through the widget `data` field.
        reference = _extract_reference(payload)
        transaction = None
        if reference:
            transaction = await self._transactions.get_by_reference(reference)
        if transaction is None:
            raise TransactionNotFound("No local transaction matches the webhook.")

        return await self._verify.by_reference(
            transaction.reference, kkiapay_transaction_id=str(kkiapay_txn_id), force=True
        )


def _extract_reference(payload: dict):
    from uuid import UUID

    raw = payload.get("reference") or payload.get("data") or {}
    if isinstance(raw, dict):
        raw = raw.get("reference")
    try:
        return UUID(str(raw)) if raw else None
    except (ValueError, TypeError):
        return None
