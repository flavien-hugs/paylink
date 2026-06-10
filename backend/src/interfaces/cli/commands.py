import asyncio

import typer
import uvicorn

from ...config.settings import settings
from ...domain.models import AdminUser, Entity
from ...infrastructure.adapters.postgres import Database
from ...infrastructure.adapters.postgres.repositories import (
    PgAdminUserRepository,
    PgEntityRepository,
)
from ...infrastructure.adapters.security import BcryptPasswordHasher, FernetCipher

app = typer.Typer(help="PayLink API management commands.")


@app.command()
def serve(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the API server."""
    uvicorn.run("src.main:app", host=host, port=port, reload=reload)


@app.command()
def seed():
    """Bootstrap the default admin user and a demo entity (idempotent)."""
    asyncio.run(_seed())


async def _seed() -> None:
    database = Database(settings.DATABASE_URL)
    hasher = BcryptPasswordHasher()
    cipher = FernetCipher(settings.FERNET_KEY)

    async with database.session() as session:
        admins = PgAdminUserRepository(session)
        entities = PgEntityRepository(session, cipher)

        email = settings.SEED_ADMIN_EMAIL.lower().strip()
        if await admins.get_by_email(email) is None:
            await admins.add(
                AdminUser(
                    email=email,
                    hashed_password=hasher.hash(settings.SEED_ADMIN_PASSWORD),
                    is_superadmin=True,
                )
            )
            typer.echo(f"Created super admin user: {email}")
        else:
            typer.echo(f"Admin user already exists: {email}")

        if await entities.get_by_slug(settings.SEED_ENTITY_SLUG) is None:
            await entities.add(
                Entity(
                    slug=settings.SEED_ENTITY_SLUG,
                    name=settings.SEED_ENTITY_NAME,
                    kkiapay_public_key=settings.SEED_KKIAPAY_PUBLIC_KEY,
                    kkiapay_private_key=settings.SEED_KKIAPAY_PRIVATE_KEY,
                    kkiapay_secret=settings.SEED_KKIAPAY_SECRET,
                    sandbox=True,
                )
            )
            typer.echo(f"Created demo entity: {settings.SEED_ENTITY_SLUG}")
        else:
            typer.echo(f"Entity already exists: {settings.SEED_ENTITY_SLUG}")

    await database.dispose()


if __name__ == "__main__":
    app()
