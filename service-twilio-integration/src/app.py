import asyncio
import traceback
import typing as t

import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from config import app_settings
from dependencies.auth import http_basic_dependency
from logger import logger
from routers.system import router as system_router
from routers.twilio import router as twilio_router

app = FastAPI(title=app_settings.name,
              version=app_settings.version,
              docs_url=None,
              redoc_url=None,
              openapi_url=None,
              )

FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")

app.include_router(system_router)
app.include_router(twilio_router)


@app.middleware("http")
async def errors_handling(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        tb_str = traceback.format_exception(type(exc), value=exc, tb=exc.__traceback__)
        logger.error(exc)
        logger.error(tb_str)
        return JSONResponse(status_code=500, content={'detail': str(exc), 'traceback': tb_str})


@app.get('/openapi.json', include_in_schema=False)
async def openapi_json(credentials=Depends(http_basic_dependency)) -> dict[str, t.Any]:
    """Protection for openapi.json path"""
    return get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        terms_of_service=app.terms_of_service,
        contact=app.contact,
        license_info=app.license_info,
        routes=app.routes,
        tags=app.openapi_tags,
        servers=app.servers,
    )


def app_start():
    config = uvicorn.Config(
        app=app, 
        host="0.0.0.0", 
        port=app_settings.port,
        )
    server = uvicorn.Server(config)
    asyncio.get_event_loop().run_until_complete(server.serve())


if __name__ == "__main__":
    app_start()
