import pytest

from src.application.dto import InitiatePaymentCommand
from src.application.use_cases import (
    HandleKkiapayWebhook,
    InitiatePayment,
    ManageEntities,
    VerifyPayment,
)
from src.application.use_cases.list_transactions import TransactionStats
from src.domain.exceptions import EntityNotFound, InvalidAmount
from src.domain.models import PaymentStatus

from .fakes import (
    FakeAdminUserRepository,
    FakeEntityRepository,
    FakeGateway,
    FakeTransactionRepository,
    make_entity,
)


@pytest.fixture
def repos():
    return FakeEntityRepository(), FakeTransactionRepository(), FakeAdminUserRepository()


async def test_initiate_payment_creates_pending_transaction(repos):
    entities, transactions, _ = repos
    entity = make_entity("sbbs")
    await entities.add(entity)

    use_case = InitiatePayment(entities, transactions)
    result = await use_case.execute(
        InitiatePaymentCommand(entity_slug="sbbs", amount=5000, customer_name="Ana")
    )

    assert result.amount == 5000
    assert result.public_key == "pub"
    stored, total = await transactions.search()
    assert total == 1
    assert stored[0].status is PaymentStatus.PENDING
    assert stored[0].reference == result.reference


async def test_initiate_payment_rejects_non_positive_amount(repos):
    entities, transactions, _ = repos
    await entities.add(make_entity("sbbs"))
    use_case = InitiatePayment(entities, transactions)
    with pytest.raises(InvalidAmount):
        await use_case.execute(InitiatePaymentCommand(entity_slug="sbbs", amount=0))


async def test_initiate_payment_unknown_entity(repos):
    entities, transactions, _ = repos
    use_case = InitiatePayment(entities, transactions)
    with pytest.raises(EntityNotFound):
        await use_case.execute(InitiatePaymentCommand(entity_slug="nope", amount=100))


async def test_verify_payment_marks_success_via_gateway(repos):
    entities, transactions, _ = repos
    entity = make_entity("sbbs")
    await entities.add(entity)
    init = InitiatePayment(entities, transactions)
    result = await init.execute(InitiatePaymentCommand(entity_slug="sbbs", amount=1000))

    gateway = FakeGateway(status=PaymentStatus.SUCCESS, amount=1000)
    verify = VerifyPayment(entities, transactions, gateway)
    txn = await verify.by_reference(result.reference, kkiapay_transaction_id="KKIA-1", force=True)

    assert txn.status is PaymentStatus.SUCCESS
    assert txn.kkiapay_transaction_id == "KKIA-1"
    assert gateway.calls == ["KKIA-1"]


async def test_verify_payment_failure_status(repos):
    entities, transactions, _ = repos
    await entities.add(make_entity("sbbs"))
    init = InitiatePayment(entities, transactions)
    result = await init.execute(InitiatePaymentCommand(entity_slug="sbbs", amount=1000))

    gateway = FakeGateway(status=PaymentStatus.FAILED)
    verify = VerifyPayment(entities, transactions, gateway)
    txn = await verify.by_reference(result.reference, kkiapay_transaction_id="KKIA-2", force=True)
    assert txn.status is PaymentStatus.FAILED


async def test_webhook_revalidates_server_side(repos):
    entities, transactions, _ = repos
    await entities.add(make_entity("sbbs"))
    init = InitiatePayment(entities, transactions)
    result = await init.execute(InitiatePaymentCommand(entity_slug="sbbs", amount=2500))

    gateway = FakeGateway(status=PaymentStatus.SUCCESS, amount=2500)
    verify = VerifyPayment(entities, transactions, gateway)
    webhook = HandleKkiapayWebhook(transactions, verify)

    txn = await webhook.execute(
        {"transactionId": "KKIA-9", "data": {"reference": str(result.reference)}}
    )
    assert txn.status is PaymentStatus.SUCCESS
    assert gateway.calls == ["KKIA-9"]


async def test_webhook_reconciles_failed_payment(repos):
    entities, transactions, _ = repos
    await entities.add(make_entity("sbbs"))
    init = InitiatePayment(entities, transactions)
    result = await init.execute(InitiatePaymentCommand(entity_slug="sbbs", amount=3000))

    # The gateway reports a real FAILED outcome; the webhook must still record it.
    gateway = FakeGateway(status=PaymentStatus.FAILED)
    verify = VerifyPayment(entities, transactions, gateway)
    webhook = HandleKkiapayWebhook(transactions, verify)

    txn = await webhook.execute(
        {"transactionId": "KKIA-FAIL", "data": {"reference": str(result.reference)}}
    )
    assert txn.status is PaymentStatus.FAILED
    assert gateway.calls == ["KKIA-FAIL"]


async def test_stats_aggregates_amounts(repos):
    entities, transactions, _ = repos
    entity = make_entity("sbbs")
    await entities.add(entity)
    init = InitiatePayment(entities, transactions)
    gateway = FakeGateway(status=PaymentStatus.SUCCESS, amount=1000)
    verify = VerifyPayment(entities, transactions, gateway)

    for amount in (1000, 2000):
        r = await init.execute(InitiatePaymentCommand(entity_slug="sbbs", amount=amount))
        gateway.amount = amount
        await verify.by_reference(r.reference, kkiapay_transaction_id=f"k{amount}", force=True)
    # one left pending
    await init.execute(InitiatePaymentCommand(entity_slug="sbbs", amount=500))

    stats = await TransactionStats(transactions).execute()
    assert stats["total"] == 3
    assert stats["success"] == 2
    assert stats["pending"] == 1
    assert stats["success_amount"] == 3000


async def test_list_transactions_text_search(repos):
    entities, transactions, _ = repos
    await entities.add(make_entity("sbbs"))
    init = InitiatePayment(entities, transactions)
    await init.execute(InitiatePaymentCommand(entity_slug="sbbs", amount=100, customer_name="Alice"))
    await init.execute(InitiatePaymentCommand(entity_slug="sbbs", amount=200, customer_name="Bob"))

    from src.application.use_cases import ListTransactions

    items, total = await ListTransactions(transactions).execute(query="alic")
    assert total == 1
    assert items[0].customer_name == "Alice"


async def test_reconcile_pending_with_supplied_id(repos):
    entities, transactions, _ = repos
    await entities.add(make_entity("sbbs"))
    init = InitiatePayment(entities, transactions)
    result = await init.execute(InitiatePaymentCommand(entity_slug="sbbs", amount=999))
    created, _ = await transactions.search()
    assert created[0].status is PaymentStatus.PENDING

    gateway = FakeGateway(status=PaymentStatus.SUCCESS, amount=999)
    verify = VerifyPayment(entities, transactions, gateway)
    # No id stored on the transaction; admin supplies it for reconciliation.
    txn = await verify.by_id(created[0].id, kkiapay_transaction_id="MANUAL-1", force=True)
    assert txn.status is PaymentStatus.SUCCESS
    assert txn.kkiapay_transaction_id == "MANUAL-1"
    assert gateway.calls == ["MANUAL-1"]


async def test_superadmin_is_protected(repos):
    _, _, admins = repos
    from src.application.use_cases import ManageAdmins
    from src.domain.exceptions import ProtectedAdmin
    from src.domain.models import AdminUser
    from src.infrastructure.adapters.security import BcryptPasswordHasher

    manage = ManageAdmins(admins, BcryptPasswordHasher())
    superadmin = AdminUser(email="boss@sbbs.local", hashed_password="x", is_superadmin=True)
    await admins.add(superadmin)

    with pytest.raises(ProtectedAdmin):
        await manage.delete(superadmin.id)
    with pytest.raises(ProtectedAdmin):
        await manage.set_active(superadmin.id, False)


async def test_manage_entities_create_and_duplicate(repos):
    entities, _, _ = repos
    manage = ManageEntities(entities)
    await manage.create(make_entity("a"))
    from src.domain.exceptions import DuplicateEntity

    with pytest.raises(DuplicateEntity):
        await manage.create(make_entity("a"))
