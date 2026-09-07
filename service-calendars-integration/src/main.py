import traceback
import typing as t

from fastapi import Depends, FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from src.routers.yclients import router as yclients_router

from src.config import APPSettings
from src.dependencies.auth import http_basic_dependency
from src.logger import logger
from src.routers.calcom import router as calcom_router
from src.routers.google_calendar import router as google_calendar_router
from src.routers.system import router as system_router
from src.schemas.service_response import ServiceResponse

app = FastAPI(title=APPSettings.APP_NAME,
              version=APPSettings.APP_VERSION,
              docs_url=None,
              redoc_url=None,
              openapi_url=None,
              )
app.include_router(system_router)
app.include_router(google_calendar_router)
app.include_router(calcom_router)

if APPSettings.DEBUG_MODE:
    @app.on_event("startup")
    def run_tests():
        import sys
        from subprocess import run
        logger.info('Start tests..')
        status = run(['pytest', '-qq'])

        if status.returncode != 0:
            logger.info('Tests failed!')
            sys.exit(status.returncode)
        logger.info('Tests passed!')


@app.middleware("http")
async def errors_handling(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        tb_str = traceback.format_exception(type(exc), value=exc, tb=exc.__traceback__)
        logger.error(exc)
        logger.error(tb_str)
        error_body = ServiceResponse(status='failure', msg=str(exc), traceback=tb_str).model_dump()
        return JSONResponse(status_code=500, content=error_body)


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
