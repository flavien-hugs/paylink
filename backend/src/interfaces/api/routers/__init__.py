__all__ = ["admin", "admin_auth", "payments", "public", "webhooks", "setup_routers"]

from fastapi import FastAPI
from . import admin, admin_auth, payments, public, webhooks
from src.config.settings import settings


def setup_routers(app: FastAPI):
    prefix = settings.API_PREFIX

    app.include_router(public.router, prefix=prefix)
    app.include_router(payments.router, prefix=prefix)
    app.include_router(webhooks.router, prefix=prefix)
    app.include_router(admin_auth.router, prefix=prefix)
    app.include_router(admin.router, prefix=prefix)
