from uuid import UUID

from ...domain.exceptions import DuplicateEntity, EntityNotFound
from ...domain.models import Entity
from ...domain.ports import EntityRepository
from ..dto import PublicEntityView


class GetPublicEntity:
    """Public branding projection — never exposes private Kkiapay credentials."""

    def __init__(self, entities: EntityRepository) -> None:
        self._entities = entities

    async def execute(self, slug: str) -> PublicEntityView:
        entity = await self._entities.get_by_slug(slug)
        if entity is None or not entity.is_active:
            raise EntityNotFound(slug)
        return PublicEntityView(
            slug=entity.slug,
            name=entity.name,
            description=entity.description,
            logo_url=entity.logo_url,
            primary_color=entity.primary_color,
            secondary_color=entity.secondary_color,
            currency=entity.currency,
            public_key=entity.kkiapay_public_key,
            sandbox=entity.sandbox,
        )


class ManageEntities:
    """Admin CRUD over entities (full record, including credentials)."""

    def __init__(self, entities: EntityRepository) -> None:
        self._entities = entities

    async def list(self) -> list[Entity]:
        return await self._entities.list()

    async def get(self, entity_id: UUID) -> Entity:
        entity = await self._entities.get(entity_id)
        if entity is None:
            raise EntityNotFound(str(entity_id))
        return entity

    async def create(self, entity: Entity) -> Entity:
        if await self._entities.get_by_slug(entity.slug) is not None:
            raise DuplicateEntity(entity.slug)
        return await self._entities.add(entity)

    async def update(self, entity_id: UUID, changes: dict) -> Entity:
        entity = await self.get(entity_id)

        new_slug = changes.get("slug")
        if new_slug and new_slug != entity.slug:
            existing = await self._entities.get_by_slug(new_slug)
            if existing is not None and existing.id != entity.id:
                raise DuplicateEntity(new_slug)

        for key, value in changes.items():
            if value is not None and hasattr(entity, key):
                setattr(entity, key, value)
        return await self._entities.update(entity)

    async def delete(self, entity_id: UUID) -> None:
        await self.get(entity_id)
        await self._entities.delete(entity_id)
