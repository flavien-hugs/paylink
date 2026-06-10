from ...domain.models import Entity, Transaction
from .schemas import EntityOut, TransactionOut


def transaction_out(txn: Transaction) -> TransactionOut:
    return TransactionOut(
        id=txn.id,
        reference=txn.reference,
        kkiapay_transaction_id=txn.kkiapay_transaction_id,
        entity_id=txn.entity_id,
        amount=txn.amount,
        currency=txn.currency,
        status=txn.status,
        customer_name=txn.customer_name,
        customer_email=txn.customer_email,
        customer_phone=txn.customer_phone,
        metadata=txn.metadata,
        created_at=txn.created_at,
        updated_at=txn.updated_at,
    )


def entity_out(entity: Entity) -> EntityOut:
    return EntityOut(
        id=entity.id,
        slug=entity.slug,
        name=entity.name,
        description=entity.description,
        logo_url=entity.logo_url,
        primary_color=entity.primary_color,
        secondary_color=entity.secondary_color,
        currency=entity.currency,
        kkiapay_public_key=entity.kkiapay_public_key,
        kkiapay_private_key=entity.kkiapay_private_key,
        kkiapay_secret=entity.kkiapay_secret,
        sandbox=entity.sandbox,
        success_url=entity.success_url,
        failure_url=entity.failure_url,
        is_active=entity.is_active,
        created_at=entity.created_at,
    )
