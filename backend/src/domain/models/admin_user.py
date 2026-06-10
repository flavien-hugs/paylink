from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class AdminUser:
    """Back-office operator able to monitor payments and manage entities."""

    email: str
    hashed_password: str
    is_active: bool = True
    # The very first (seeded) account is the super administrator: it alone can
    # manage other accounts, and it cannot be deleted or deactivated.
    is_superadmin: bool = False
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
