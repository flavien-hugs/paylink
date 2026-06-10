from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ....application.dto import InitiatePaymentCommand
from ....domain.exceptions import EntityNotFound, InvalidAmount, TransactionNotFound
from ..converters import transaction_out
from ..deps import Services, get_services
from ..schemas import InitiatePaymentIn, InitiatePaymentOut, TransactionOut, VerifyPaymentIn

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/{slug}/initiate", response_model=InitiatePaymentOut, status_code=status.HTTP_201_CREATED)
async def initiate_payment(
    slug: str, body: InitiatePaymentIn, services: Services = Depends(get_services)
):
    command = InitiatePaymentCommand(
        entity_slug=slug,
        amount=body.amount,
        customer_name=body.customer_name,
        customer_email=str(body.customer_email) if body.customer_email else None,
        customer_phone=body.customer_phone,
        metadata=body.metadata,
    )
    try:
        result = await services.initiate_payment.execute(command)
    except InvalidAmount as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found.")
    return InitiatePaymentOut(**result.__dict__)


@router.post("/{reference}/verify", response_model=TransactionOut)
async def verify_payment(
    reference: UUID, body: VerifyPaymentIn, services: Services = Depends(get_services)
):
    """Called by the payment page after the Kkiapay widget returns."""
    try:
        txn = await services.verify_payment.by_reference(
            reference, kkiapay_transaction_id=body.kkiapay_transaction_id, force=True
        )
    except TransactionNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")
    return transaction_out(txn)
