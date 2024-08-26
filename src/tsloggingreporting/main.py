"""The main application factory for the ts_logging_reporting service.

Notes
-----
Be aware that, following the normal pattern for FastAPI services, the app is
constructed when this module is loaded and is not deferred until a function is
called.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from importlib.metadata import metadata, version

from fastapi import FastAPI
from safir.dependencies.http_client import http_client_dependency
from safir.logging import configure_logging, configure_uvicorn_logging
from safir.middleware.x_forwarded import XForwardedMiddleware

from .config import config
from .handlers.external import external_router
from .handlers.internal import internal_router

__all__ = ["app"]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Set up and tear down the application."""
    # Any code here will be run when the application starts up.

    yield

    # Any code here will be run when the application shuts down.
    await http_client_dependency.aclose()


configure_logging(
    profile=config.profile,
    log_level=config.log_level,
    name="tsloggingreporting",
)
configure_uvicorn_logging(config.log_level)

app = FastAPI(
    title="ts_logging_reporting",
    description=metadata("ts_logging_reporting")["Summary"],
    version=version("ts_logging_reporting"),
    openapi_url=f"{config.path_prefix}/openapi.json",
    docs_url=f"{config.path_prefix}/docs",
    redoc_url=f"{config.path_prefix}/redoc",
    lifespan=lifespan,
)
"""The main FastAPI application for ts_logging_reporting."""

# Attach the routers.
app.include_router(internal_router)
app.include_router(external_router, prefix=f"{config.path_prefix}")

# Add middleware.
app.add_middleware(XForwardedMiddleware)
