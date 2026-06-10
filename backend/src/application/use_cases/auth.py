from ...domain.exceptions import InvalidCredentials
from ...domain.ports import AdminUserRepository, PasswordHasher, TokenIssuer


class AuthenticateAdmin:
    def __init__(
        self,
        admins: AdminUserRepository,
        hasher: PasswordHasher,
        tokens: TokenIssuer,
    ) -> None:
        self._admins = admins
        self._hasher = hasher
        self._tokens = tokens

    async def execute(self, email: str, password: str) -> str:
        user = await self._admins.get_by_email(email.lower().strip())
        if user is None or not user.is_active:
            raise InvalidCredentials("Invalid email or password.")
        if not self._hasher.verify(password, user.hashed_password):
            raise InvalidCredentials("Invalid email or password.")
        return self._tokens.issue(
            str(user.id), claims={"email": user.email, "is_superadmin": user.is_superadmin}
        )
