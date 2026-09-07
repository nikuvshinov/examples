import secrets
from time import sleep

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader, HTTPBasic, HTTPBasicCredentials

from config import app_settings

http_basic_auth_scheme = HTTPBasic()
api_key_auth_scheme = APIKeyHeader(name='xi-api-key')


def http_basic_dependency(credentials: HTTPBasicCredentials = Security(http_basic_auth_scheme)):
    correct_username = secrets.compare_digest(credentials.username, app_settings.username)
    correct_password = secrets.compare_digest(credentials.password, app_settings.password)

    if not (correct_username and correct_password):
        sleep(1)
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


def api_key_dependency(key: str = Security(api_key_auth_scheme)):
    if key != app_settings.api_key:
        sleep(1)
        raise HTTPException(
            status_code=401,
            detail='Invalid or missing API Key',
        )
