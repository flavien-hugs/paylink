import bcrypt


class BcryptPasswordHasher:
    """
    `PasswordHasher` port implementation using the `bcrypt` library directly.

    We avoid passlib here: passlib 1.7.x is incompatible with bcrypt >= 4.1 (it
    crashes on an internal self-test). bcrypt caps secrets at 72 bytes, so we
    truncate explicitly before hashing/verifying.
    """

    @staticmethod
    def _prepare(plain: str) -> bytes:
        return plain.encode("utf-8")[:72]

    def hash(self, plain: str) -> str:
        return bcrypt.hashpw(self._prepare(plain), bcrypt.gensalt()).decode("utf-8")

    def verify(self, plain: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(self._prepare(plain), hashed.encode("utf-8"))
        except (ValueError, TypeError):
            return False
