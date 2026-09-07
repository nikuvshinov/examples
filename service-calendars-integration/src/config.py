from src.utils.common import EnvVariable


class APPSettings:
    APP_NAME = 'service-calendars-integration'
    APP_VERSION = '0.0.2'
    DEBUG_MODE = EnvVariable(False)

    APP_USERNAME = EnvVariable('admin')
    APP_PASSWORD = EnvVariable('admin')
    SERVICE_API_KEY_HEADER = EnvVariable('xi-api-key')
    SERVICE_API_KEY = EnvVariable('admin')


class GoogleAppCredentials:
    GOOGLE_CLIENT_ID = EnvVariable(default='admin')
    GOOGLE_CLIENT_SECRET = EnvVariable(default='admin')
