import secrets
from time import sleep

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader, HTTPBasic, HTTPBasicCredentials

from src.config import APPSettings

http_basic_auth_scheme = HTTPBasic()
api_key_auth_scheme = APIKeyHeader(name=APPSettings.SERVICE_API_KEY_HEADER)


def http_basic_dependency(credentials: HTTPBasicCredentials = Security(http_basic_auth_scheme)):
    correct_username = secrets.compare_digest(credentials.username, APPSettings.APP_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, APPSettings.APP_PASSWORD)

    if not (correct_username and correct_password):
        sleep(1)
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


def api_key_dependency(key: str = Security(api_key_auth_scheme)):
    if key != APPSettings.SERVICE_API_KEY:
        sleep(1)
        raise HTTPException(
            status_code=401,
            detail='Invalid or missing API Key',
        )
