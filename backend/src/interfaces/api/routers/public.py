from fastapi import APIRouter, Depends, HTTPException, status

from ....domain.exceptions import EntityNotFound
from ..deps import Services, get_services
from ..schemas import PublicEntityOut

router = APIRouter(prefix="/entities", tags=["public"])


@router.get("/{slug}", response_model=PublicEntityOut)
async def get_entity_branding(slug: str, services: Services = Depends(get_services)):
    """Public branding for the payment page. Never returns private credentials."""
    try:
        view = await services.get_public_entity.execute(slug)
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found.")
    return PublicEntityOut(**view.__dict__)
