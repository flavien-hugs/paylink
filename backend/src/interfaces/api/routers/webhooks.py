import logging

from fastapi import APIRouter, Depends, Request

from ....domain.exceptions import DomainError
from ..deps import Services, get_services

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/kkiapay")
async def kkiapay_webhook(request: Request, services: Services = Depends(get_services)):
    """
    Receive Kkiapay notifications. We always return 200 so the provider does not
    keep retrying on transactions we cannot match; the payload is never trusted
    for status — we re-verify server-side.
    """
    payload = await request.json()
    try:
        txn = await services.handle_webhook.execute(payload)
        return {"received": True, "reference": str(txn.reference), "status": txn.status.value}
    except DomainError as exc:
        logger.info("Ignoring unmatched/invalid Kkiapay webhook: %s", exc)
        return {"received": True, "matched": False}
