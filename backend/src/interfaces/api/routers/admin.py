import csv
import io
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from ....domain.exceptions import (
    AdminNotFound,
    DuplicateAdmin,
    DuplicateEntity,
    EntityNotFound,
    InvalidCredentials,
    ProtectedAdmin,
    TransactionNotFound,
)
from ....domain.models import Entity, PaymentStatus
from ..converters import entity_out, transaction_out
from ..deps import Services, get_services, require_admin, require_superadmin
from ..schemas import (
    AdminUserIn,
    AdminUserOut,
    AdminUserUpdateIn,
    ChangePasswordIn,
    DailyPointOut,
    EntityIn,
    EntityOut,
    EntityStatOut,
    EntityUpdateIn,
    PaginatedTransactions,
    ReverifyIn,
    StatsOut,
    StatsReportOut,
    TransactionOut,
)

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


# ----- Transactions -----
@router.get("/transactions", response_model=PaginatedTransactions)
async def list_transactions(
    services: Services = Depends(get_services),
    entity_id: UUID | None = None,
    status_filter: PaymentStatus | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None),
    sort: str = Query(default="desc", pattern="^(asc|desc)$"),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    items, total = await services.list_transactions.execute(
        entity_id=entity_id,
        status=status_filter,
        query=search,
        date_from=date_from,
        date_to=date_to,
        order=sort,
        limit=limit,
        offset=offset,
    )
    return PaginatedTransactions(
        items=[transaction_out(t) for t in items], total=total, limit=limit, offset=offset
    )


@router.get("/transactions/export")
async def export_transactions(
    services: Services = Depends(get_services),
    entity_id: UUID | None = None,
    status_filter: PaymentStatus | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None),
):
    """CSV export of transactions (respects the same filters as the list)."""
    items, _ = await services.list_transactions.execute(
        entity_id=entity_id, status=status_filter, query=search, limit=10000, offset=0
    )
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "reference",
            "kkiapay_transaction_id",
            "status",
            "amount",
            "currency",
            "customer_name",
            "customer_email",
            "customer_phone",
            "created_at",
            "updated_at",
        ]
    )
    for t in items:
        writer.writerow(
            [
                t.reference,
                t.kkiapay_transaction_id or "",
                t.status.value,
                t.amount,
                t.currency,
                t.customer_name or "",
                t.customer_email or "",
                t.customer_phone or "",
                t.created_at.isoformat(),
                t.updated_at.isoformat(),
            ]
        )
    filename = f"transactions-{datetime.utcnow():%Y%m%d-%H%M%S}.csv"
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/transactions/{transaction_id}", response_model=TransactionOut)
async def get_transaction(transaction_id: UUID, services: Services = Depends(get_services)):
    try:
        txn = await services.get_transaction.execute(transaction_id)
    except TransactionNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")
    return transaction_out(txn)


@router.post("/transactions/{transaction_id}/reverify", response_model=TransactionOut)
async def reverify_transaction(
    transaction_id: UUID,
    body: ReverifyIn | None = Body(default=None),
    services: Services = Depends(get_services),
):
    try:
        txn = await services.verify_payment.by_id(
            transaction_id,
            kkiapay_transaction_id=body.kkiapay_transaction_id if body else None,
            force=True,
        )
    except TransactionNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")
    return transaction_out(txn)


@router.get("/stats", response_model=StatsOut)
async def stats(entity_id: UUID | None = None, services: Services = Depends(get_services)):
    return StatsOut(**await services.transaction_stats.execute(entity_id=entity_id))


@router.get("/stats/report", response_model=StatsReportOut)
async def stats_report(days: int = Query(default=14, ge=1, le=90), services: Services = Depends(get_services)):
    overall = await services.transaction_stats.execute()
    entities = await services.manage_entities.list()
    by_entity = []
    for e in entities:
        s = await services.transaction_stats.execute(entity_id=e.id)
        by_entity.append(EntityStatOut(entity_id=e.id, name=e.name, **s))
    daily = [DailyPointOut(**p) for p in await services.transactions_repo.daily_series(days=days)]
    return StatsReportOut(overall=StatsOut(**overall), by_entity=by_entity, daily=daily)


# ----- Admin users (super administrator only) -----
@router.get("/users", response_model=list[AdminUserOut], dependencies=[Depends(require_superadmin)])
async def list_users(services: Services = Depends(get_services)):
    return [AdminUserOut(**u.__dict__) for u in await services.manage_admins.list()]


@router.post(
    "/users",
    response_model=AdminUserOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_superadmin)],
)
async def create_user(body: AdminUserIn, services: Services = Depends(get_services)):
    try:
        user = await services.manage_admins.create(str(body.email), body.password, body.is_active)
    except DuplicateAdmin:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists.")
    return AdminUserOut(**user.__dict__)


@router.put("/users/{user_id}", response_model=AdminUserOut, dependencies=[Depends(require_superadmin)])
async def update_user(
    user_id: UUID, body: AdminUserUpdateIn, services: Services = Depends(get_services)
):
    try:
        user = await services.manage_admins.update(
            user_id,
            email=str(body.email) if body.email else None,
            password=body.password,
            is_active=body.is_active,
        )
    except AdminNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    except DuplicateAdmin:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists.")
    except ProtectedAdmin as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    return AdminUserOut(**user.__dict__)


@router.post(
    "/users/{user_id}/activate", response_model=AdminUserOut, dependencies=[Depends(require_superadmin)]
)
async def activate_user(user_id: UUID, services: Services = Depends(get_services)):
    try:
        user = await services.manage_admins.set_active(user_id, True)
    except AdminNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return AdminUserOut(**user.__dict__)


@router.post(
    "/users/{user_id}/deactivate", response_model=AdminUserOut, dependencies=[Depends(require_superadmin)]
)
async def deactivate_user(user_id: UUID, services: Services = Depends(get_services)):
    try:
        user = await services.manage_admins.set_active(user_id, False)
    except AdminNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    except ProtectedAdmin as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    return AdminUserOut(**user.__dict__)


@router.delete(
    "/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_superadmin)]
)
async def delete_user(user_id: UUID, services: Services = Depends(get_services)):
    try:
        await services.manage_admins.delete(user_id)
    except AdminNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    except ProtectedAdmin as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


# ----- Current account (settings) -----
@router.get("/me", response_model=AdminUserOut)
async def me(admin_id: str = Depends(require_admin), services: Services = Depends(get_services)):
    try:
        user = await services.manage_admins.get(UUID(admin_id))
    except (AdminNotFound, ValueError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return AdminUserOut(**user.__dict__)


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_my_password(
    body: ChangePasswordIn,
    admin_id: str = Depends(require_admin),
    services: Services = Depends(get_services),
):
    try:
        await services.change_password.execute(UUID(admin_id), body.current_password, body.new_password)
    except InvalidCredentials as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except (AdminNotFound, ValueError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")


# ----- Entities CRUD -----
@router.get("/entities", response_model=list[EntityOut])
async def list_entities(services: Services = Depends(get_services)):
    return [entity_out(e) for e in await services.manage_entities.list()]


@router.get("/entities/{entity_id}", response_model=EntityOut)
async def get_entity(entity_id: UUID, services: Services = Depends(get_services)):
    try:
        return entity_out(await services.manage_entities.get(entity_id))
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found.")


@router.post("/entities", response_model=EntityOut, status_code=status.HTTP_201_CREATED)
async def create_entity(body: EntityIn, services: Services = Depends(get_services)):
    entity = Entity(**body.model_dump())
    try:
        created = await services.manage_entities.create(entity)
    except DuplicateEntity:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug already exists.")
    return entity_out(created)


@router.put("/entities/{entity_id}", response_model=EntityOut)
async def update_entity(
    entity_id: UUID, body: EntityUpdateIn, services: Services = Depends(get_services)
):
    try:
        updated = await services.manage_entities.update(entity_id, body.model_dump(exclude_unset=True))
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found.")
    except DuplicateEntity:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug already exists.")
    return entity_out(updated)


@router.delete("/entities/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity(entity_id: UUID, services: Services = Depends(get_services)):
    try:
        await services.manage_entities.delete(entity_id)
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found.")
