from fastapi import APIRouter, Depends, HTTPException, status

from ....domain.exceptions import InvalidCredentials
from ..deps import Services, get_services
from ..schemas import LoginIn, TokenOut

router = APIRouter(prefix="/admin", tags=["admin-auth"])


@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn, services: Services = Depends(get_services)):
    try:
        token = await services.authenticate_admin.execute(str(body.email), body.password)
    except InvalidCredentials as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return TokenOut(access_token=token)
