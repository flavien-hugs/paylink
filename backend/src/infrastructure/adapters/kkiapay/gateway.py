import logging

import httpx

from ....domain.models import Entity, GatewayResult, PaymentStatus

logger = logging.getLogger(__name__)


class KkiapayGateway:
    """
    `PaymentGateway` implementation talking to Kkiapay's verification API.

    Server-side verification is authoritative: we POST the transaction id to
    `/api/v1/transactions/status` with the entity's API keys and read back the
    real status and amount.
    """

    def __init__(self, api_url: str, sandbox_api_url: str, timeout: float = 15.0) -> None:
        self._api_url = api_url.rstrip("/")
        self._sandbox_api_url = sandbox_api_url.rstrip("/")
        self._timeout = timeout

    def _base_url(self, entity: Entity) -> str:
        return self._sandbox_api_url if entity.sandbox else self._api_url

    async def verify(self, transaction_id: str, *, entity: Entity) -> GatewayResult:
        url = f"{self._base_url(entity)}/api/v1/transactions/status"
        headers = {
            "x-api-key": entity.kkiapay_public_key,
            "x-private-key": entity.kkiapay_private_key,
            "x-secret-key": entity.kkiapay_secret,
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, json={"transactionId": transaction_id}, headers=headers)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            logger.warning("Kkiapay verify failed for %s: %s", transaction_id, exc)
            return GatewayResult(status=PaymentStatus.PENDING, transaction_id=transaction_id, raw={"error": str(exc)})

        status = PaymentStatus.from_kkiapay(data.get("status"))
        amount = data.get("amount")
        return GatewayResult(
            status=status,
            amount=int(amount) if amount is not None else None,
            transaction_id=str(data.get("transactionId") or transaction_id),
            raw=data,
        )
