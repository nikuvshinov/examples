from fastapi import APIRouter, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse

from src.config import APPSettings
from src.dependencies.auth import http_basic_dependency

router = APIRouter(tags=["system"])


@router.get('/heathcheck')
def heathcheck() -> JSONResponse:
    return JSONResponse({"message": "I'm alive!"})


@router.get('/docs', include_in_schema=False)
async def docs(credentials=Depends(http_basic_dependency)) -> HTMLResponse:
    """Protection for docs path"""
    return get_swagger_ui_html(openapi_url='/openapi.json', title=APPSettings.APP_NAME)
