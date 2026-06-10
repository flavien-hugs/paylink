from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config.settings import settings
from .interfaces.api.deps import Container
from .interfaces.api.routers import setup_routers

__version__ = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.container = Container.build(settings)
    yield
    await app.state.container.database.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        docs_url="/paylink/docs" if settings.HIDE_DOCS is False else None, 
        redoc_url="/paylink/redoc" if settings.HIDE_DOCS is False else None, 
        openapi_url="/paylink/openapi.json" if settings.HIDE_DOCS is False else None, 
        version=__version__,
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_routers(app)

    @app.get("/health", tags=["health"])
    async def health():
        return {"status": "ok", "version": __version__}

    return app


app = create_app()
