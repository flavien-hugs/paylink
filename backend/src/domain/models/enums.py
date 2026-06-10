from enum import Enum, unique


@unique
class PaymentStatus(str, Enum):
    """Lifecycle status of a payment transaction."""

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

    @classmethod
    def from_kkiapay(cls, raw_status: str | None) -> "PaymentStatus":
        """Map a Kkiapay transaction status onto our domain status."""
        normalized = (raw_status or "").strip().upper()
        if normalized in {"SUCCESS", "SUCCESSFUL", "PAID", "COMPLETED"}:
            return cls.SUCCESS
        if normalized in {"FAILED", "FAILURE", "DECLINED", "CANCELLED", "INSUFFICIENT_FUNDS"}:
            return cls.FAILED
        return cls.PENDING
