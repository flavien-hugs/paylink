import types

import pytest
from fastapi.testclient import TestClient

from src.application.use_cases import (
    AuthenticateAdmin,
    ChangePassword,
    GetPublicEntity,
    GetTransaction,
    HandleKkiapayWebhook,
    InitiatePayment,
    ListTransactions,
    ManageAdmins,
    ManageEntities,
    TransactionStats,
    VerifyPayment,
)
from src.infrastructure.adapters.security import BcryptPasswordHasher, JoseTokenIssuer
from src.interfaces.api.deps import get_services, require_admin, require_superadmin
from src.main import create_app

from .fakes import (
    FakeAdminUserRepository,
    FakeEntityRepository,
    FakeGateway,
    FakeTransactionRepository,
    make_entity,
)


@pytest.fixture
def context():
    entities = FakeEntityRepository()
    transactions = FakeTransactionRepository()
    admins = FakeAdminUserRepository()
    gateway = FakeGateway()
    hasher = BcryptPasswordHasher()
    tokens = JoseTokenIssuer("test-secret")

    services = types.SimpleNamespace(
        entities_repo=entities,
        transactions_repo=transactions,
        initiate_payment=InitiatePayment(entities, transactions),
        verify_payment=VerifyPayment(entities, transactions, gateway),
        list_transactions=ListTransactions(transactions),
        get_transaction=GetTransaction(transactions),
        transaction_stats=TransactionStats(transactions),
        get_public_entity=GetPublicEntity(entities),
        manage_entities=ManageEntities(entities),
        manage_admins=ManageAdmins(admins, hasher),
        change_password=ChangePassword(admins, hasher),
        authenticate_admin=AuthenticateAdmin(admins, hasher, tokens),
    )
    services.handle_webhook = HandleKkiapayWebhook(transactions, services.verify_payment)

    app = create_app()
    app.dependency_overrides[get_services] = lambda: services
    app.dependency_overrides[require_admin] = lambda: "test-admin"
    app.dependency_overrides[require_superadmin] = lambda: "test-admin"
    client = TestClient(app)
    return client, entities, gateway


def seed_entity(entities: FakeEntityRepository, slug: str = "sbbs"):
    """Insert directly into the in-memory store (no event loop needed)."""
    entity = make_entity(slug)
    entities._by_id[entity.id] = entity
    return entity


def test_public_entity_hides_private_keys(context):
    client, entities, _ = context
    seed_entity(entities)

    res = client.get("/api/entities/sbbs")
    assert res.status_code == 200
    body = res.json()
    assert body["public_key"] == "pub"
    assert "kkiapay_private_key" not in body
    assert "kkiapay_secret" not in body


def test_full_payment_flow(context):
    client, entities, gateway = context
    seed_entity(entities)

    init = client.post("/api/payments/sbbs/initiate", json={"amount": 7500})
    assert init.status_code == 201
    reference = init.json()["reference"]

    verify = client.post(
        f"/api/payments/{reference}/verify", json={"kkiapay_transaction_id": "KKIA-XYZ"}
    )
    assert verify.status_code == 200
    assert verify.json()["status"] == "SUCCESS"
    assert gateway.calls == ["KKIA-XYZ"]


def test_initiate_rejects_zero_amount(context):
    client, entities, _ = context
    seed_entity(entities)
    res = client.post("/api/payments/sbbs/initiate", json={"amount": 0})
    assert res.status_code == 422


def test_unknown_entity_returns_404(context):
    client, _, _ = context
    res = client.get("/api/entities/nope")
    assert res.status_code == 404


def test_admin_stats_endpoint(context):
    client, _, _ = context
    res = client.get("/api/admin/stats")
    assert res.status_code == 200
    assert res.json()["total"] == 0


def test_admin_users_crud(context):
    client, _, _ = context
    created = client.post(
        "/api/admin/users", json={"email": "ops@example.com", "password": "secret123"}
    )
    assert created.status_code == 201
    uid = created.json()["id"]
    assert created.json()["is_active"] is True

    listed = client.get("/api/admin/users")
    assert any(u["email"] == "ops@example.com" for u in listed.json())

    off = client.post(f"/api/admin/users/{uid}/deactivate")
    assert off.status_code == 200
    assert off.json()["is_active"] is False

    dup = client.post(
        "/api/admin/users", json={"email": "ops@example.com", "password": "secret123"}
    )
    assert dup.status_code == 409


def test_stats_report_and_export(context):
    client, entities, _ = context
    seed_entity(entities)
    client.post("/api/payments/sbbs/initiate", json={"amount": 1500, "customer_name": "Zoe"})

    report = client.get("/api/admin/stats/report")
    assert report.status_code == 200
    body = report.json()
    assert body["overall"]["total"] == 1
    assert len(body["by_entity"]) == 1

    export = client.get("/api/admin/transactions/export")
    assert export.status_code == 200
    assert "text/csv" in export.headers["content-type"]
    assert "reference" in export.text
    assert "Zoe" in export.text
