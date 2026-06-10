from cryptography.fernet import Fernet


class FernetCipher:
    """
    Symmetric encryption for Kkiapay secret credentials at rest. Encrypts on
    write to Postgres and decrypts on read, so secrets never sit in plaintext.
    """

    def __init__(self, key: str) -> None:
        self._fernet = Fernet(key.encode() if isinstance(key, str) else key)

    def encrypt(self, plain: str | None) -> str | None:
        if plain is None:
            return None
        return self._fernet.encrypt(plain.encode()).decode()

    def decrypt(self, token: str | None) -> str | None:
        if token is None:
            return None
        return self._fernet.decrypt(token.encode()).decode()
