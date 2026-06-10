from ....domain.models import AdminUser, Entity, PaymentStatus, Transaction
from ..security import FernetCipher
from .orm import AdminUserRow, EntityRow, TransactionRow


def entity_to_domain(row: EntityRow, cipher: FernetCipher) -> Entity:
    return Entity(
        id=row.id,
        slug=row.slug,
        name=row.name,
        description=row.description,
        logo_url=row.logo_url,
        primary_color=row.primary_color,
        secondary_color=row.secondary_color,
        currency=row.currency,
        kkiapay_public_key=cipher.decrypt(row.kkiapay_public_key),
        kkiapay_private_key=cipher.decrypt(row.kkiapay_private_key),
        kkiapay_secret=cipher.decrypt(row.kkiapay_secret),
        sandbox=row.sandbox,
        success_url=row.success_url,
        failure_url=row.failure_url,
        is_active=row.is_active,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def apply_entity_to_row(entity: Entity, row: EntityRow, cipher: FernetCipher) -> EntityRow:
    row.slug = entity.slug
    row.name = entity.name
    row.description = entity.description
    row.logo_url = entity.logo_url
    row.primary_color = entity.primary_color
    row.secondary_color = entity.secondary_color
    row.currency = entity.currency
    row.kkiapay_public_key = cipher.encrypt(entity.kkiapay_public_key)
    row.kkiapay_private_key = cipher.encrypt(entity.kkiapay_private_key)
    row.kkiapay_secret = cipher.encrypt(entity.kkiapay_secret)
    row.sandbox = entity.sandbox
    row.success_url = entity.success_url
    row.failure_url = entity.failure_url
    row.is_active = entity.is_active
    return row


def transaction_to_domain(row: TransactionRow) -> Transaction:
    return Transaction(
        id=row.id,
        reference=row.reference,
        kkiapay_transaction_id=row.kkiapay_transaction_id,
        entity_id=row.entity_id,
        amount=row.amount,
        currency=row.currency,
        status=PaymentStatus(row.status),
        customer_name=row.customer_name,
        customer_email=row.customer_email,
        customer_phone=row.customer_phone,
        metadata=row.transaction_metadata or {},
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def apply_transaction_to_row(txn: Transaction, row: TransactionRow) -> TransactionRow:
    row.reference = txn.reference
    row.kkiapay_transaction_id = txn.kkiapay_transaction_id
    row.entity_id = txn.entity_id
    row.amount = txn.amount
    row.currency = txn.currency
    row.status = txn.status.value
    row.customer_name = txn.customer_name
    row.customer_email = txn.customer_email
    row.customer_phone = txn.customer_phone
    row.transaction_metadata = txn.metadata
    return row


def admin_to_domain(row: AdminUserRow) -> AdminUser:
    return AdminUser(
        id=row.id,
        email=row.email,
        hashed_password=row.hashed_password,
        is_active=row.is_active,
        is_superadmin=row.is_superadmin,
        created_at=row.created_at,
    )
