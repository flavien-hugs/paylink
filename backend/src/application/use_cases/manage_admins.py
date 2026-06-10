from uuid import UUID

from ...domain.exceptions import (
    AdminNotFound,
    DuplicateAdmin,
    InvalidCredentials,
    ProtectedAdmin,
)
from ...domain.models import AdminUser
from ...domain.ports import AdminUserRepository, PasswordHasher


class ManageAdmins:
    """Admin CRUD over back-office user accounts."""

    def __init__(self, admins: AdminUserRepository, hasher: PasswordHasher) -> None:
        self._admins = admins
        self._hasher = hasher

    async def list(self) -> list[AdminUser]:
        return await self._admins.list()

    async def get(self, user_id: UUID) -> AdminUser:
        user = await self._admins.get(user_id)
        if user is None:
            raise AdminNotFound(str(user_id))
        return user

    async def create(self, email: str, password: str, is_active: bool = True) -> AdminUser:
        email = email.lower().strip()
        if await self._admins.get_by_email(email) is not None:
            raise DuplicateAdmin(email)
        user = AdminUser(
            email=email, hashed_password=self._hasher.hash(password), is_active=is_active
        )
        return await self._admins.add(user)

    async def update(
        self,
        user_id: UUID,
        *,
        email: str | None = None,
        password: str | None = None,
        is_active: bool | None = None,
    ) -> AdminUser:
        user = await self.get(user_id)
        if email and email.lower().strip() != user.email:
            new_email = email.lower().strip()
            existing = await self._admins.get_by_email(new_email)
            if existing is not None and existing.id != user.id:
                raise DuplicateAdmin(new_email)
            user.email = new_email
        if password:
            user.hashed_password = self._hasher.hash(password)
        if is_active is not None:
            user.is_active = is_active
        return await self._admins.update(user)

    async def set_active(self, user_id: UUID, is_active: bool) -> AdminUser:
        user = await self.get(user_id)
        if user.is_superadmin and not is_active:
            raise ProtectedAdmin("The super administrator cannot be deactivated.")
        return await self.update(user_id, is_active=is_active)

    async def delete(self, user_id: UUID) -> None:
        user = await self.get(user_id)
        if user.is_superadmin:
            raise ProtectedAdmin("The super administrator cannot be deleted.")
        await self._admins.delete(user_id)


class ChangePassword:
    """Let the currently authenticated admin change their own password."""

    def __init__(self, admins: AdminUserRepository, hasher: PasswordHasher) -> None:
        self._admins = admins
        self._hasher = hasher

    async def execute(self, user_id: UUID, current_password: str, new_password: str) -> None:
        user = await self._admins.get(user_id)
        if user is None:
            raise AdminNotFound(str(user_id))
        if not self._hasher.verify(current_password, user.hashed_password):
            raise InvalidCredentials("Current password is incorrect.")
        user.hashed_password = self._hasher.hash(new_password)
        await self._admins.update(user)
