class DomainError(Exception):
    """Base class for domain-level errors."""


class EntityNotFound(DomainError):
    pass


class TransactionNotFound(DomainError):
    pass


class InvalidAmount(DomainError):
    pass


class InvalidCredentials(DomainError):
    pass


class WebhookVerificationError(DomainError):
    pass


class DuplicateEntity(DomainError):
    pass


class AdminNotFound(DomainError):
    pass


class DuplicateAdmin(DomainError):
    pass


class ProtectedAdmin(DomainError):
    """Raised when attempting a forbidden action on the super administrator."""

    pass
