from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class EntityRow(Base):
    __tablename__ = "entities"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    primary_color: Mapped[str] = mapped_column(String(16), default="#2563eb")
    secondary_color: Mapped[str] = mapped_column(String(16), default="#1e293b")
    currency: Mapped[str] = mapped_column(String(8), default="XOF")
    # Stored encrypted at rest (Fernet).
    kkiapay_public_key: Mapped[str] = mapped_column(Text, nullable=False)
    kkiapay_private_key: Mapped[str] = mapped_column(Text, nullable=False)
    kkiapay_secret: Mapped[str] = mapped_column(Text, nullable=False)
    sandbox: Mapped[bool] = mapped_column(Boolean, default=True)
    success_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    failure_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    transactions: Mapped[list["TransactionRow"]] = relationship(back_populates="entity")


class TransactionRow(Base):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    reference: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), unique=True, index=True, default=uuid4)
    kkiapay_transaction_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    entity_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), index=True
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="XOF")
    status: Mapped[str] = mapped_column(String(16), default="PENDING", index=True)
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    transaction_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    entity: Mapped["EntityRow"] = relationship(back_populates="transactions")


class AdminUserRow(Base):
    __tablename__ = "admin_users"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superadmin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
