from collections.abc import AsyncIterator
from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.use_cases import (
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
from ...config.settings import Settings
from ...domain.exceptions import InvalidCredentials
from ...infrastructure.adapters.kkiapay import KkiapayGateway
from ...infrastructure.adapters.postgres import (
    Database,
    PgAdminUserRepository,
    PgEntityRepository,
    PgTransactionRepository,
)
from ...infrastructure.adapters.security import BcryptPasswordHasher, FernetCipher, JoseTokenIssuer


@dataclass
class Container:
    """Application singletons (composition root), stored on app.state."""

    settings: Settings
    database: Database
    cipher: FernetCipher
    hasher: BcryptPasswordHasher
    tokens: JoseTokenIssuer
    gateway: KkiapayGateway

    @classmethod
    def build(cls, settings: Settings) -> "Container":
        return cls(
            settings=settings,
            database=Database(settings.DATABASE_URL),
            cipher=FernetCipher(settings.FERNET_KEY),
            hasher=BcryptPasswordHasher(),
            tokens=JoseTokenIssuer(
                settings.JWT_SECRET, settings.JWT_ALGORITHM, settings.JWT_EXPIRE_MINUTES
            ),
            gateway=KkiapayGateway(settings.KKIAPAY_API_URL, settings.KKIAPAY_SANDBOX_API_URL),
        )


def get_container(request: Request) -> Container:
    return request.app.state.container


async def get_session(container: Container = Depends(get_container)) -> AsyncIterator[AsyncSession]:
    async with container.database.session() as session:
        yield session


class Services:
    """Per-request facade building use cases over a live session."""

    def __init__(self, session: AsyncSession, container: Container) -> None:
        entities = PgEntityRepository(session, container.cipher)
        transactions = PgTransactionRepository(session)
        admins = PgAdminUserRepository(session)
        gateway = container.gateway

        self.entities_repo = entities
        self.transactions_repo = transactions
        self.initiate_payment = InitiatePayment(entities, transactions)
        self.verify_payment = VerifyPayment(entities, transactions, gateway)
        self.handle_webhook = HandleKkiapayWebhook(transactions, self.verify_payment)
        self.list_transactions = ListTransactions(transactions)
        self.get_transaction = GetTransaction(transactions)
        self.transaction_stats = TransactionStats(transactions)
        self.get_public_entity = GetPublicEntity(entities)
        self.manage_entities = ManageEntities(entities)
        self.manage_admins = ManageAdmins(admins, container.hasher)
        self.change_password = ChangePassword(admins, container.hasher)
        self.authenticate_admin = AuthenticateAdmin(admins, container.hasher, container.tokens)


def get_services(
    session: AsyncSession = Depends(get_session),
    container: Container = Depends(get_container),
) -> Services:
    return Services(session, container)


_bearer = HTTPBearer(auto_error=False)


def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    container: Container = Depends(get_container),
) -> str:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token.")
    try:
        payload = container.tokens.decode(credentials.credentials)
    except InvalidCredentials as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return payload.get("sub", "")


async def require_superadmin(
    admin_id: str = Depends(require_admin),
    services: "Services" = Depends(get_services),
) -> str:
    """Authoritative DB check that the current account is the super administrator."""
    from uuid import UUID

    from ...domain.exceptions import AdminNotFound

    try:
        user = await services.manage_admins.get(UUID(admin_id))
    except (AdminNotFound, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown account.")
    if not user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Réservé au super administrateur.",
        )
    return admin_id
