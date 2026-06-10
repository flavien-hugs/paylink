from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from ....domain.exceptions import InvalidCredentials


class JoseTokenIssuer:
    """`TokenIssuer` port implementation backed by python-jose (HS256)."""

    def __init__(self, secret: str, algorithm: str = "HS256", expire_minutes: int = 720) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    def issue(self, subject: str, claims: dict | None = None) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(minutes=self._expire_minutes),
            **(claims or {}),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode(self, token: str) -> dict:
        try:
            return jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except JWTError as exc:
            raise InvalidCredentials("Invalid or expired token.") from exc
