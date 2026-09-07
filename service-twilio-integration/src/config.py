from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='../.env', env_prefix='app_', extra='ignore')
    port: int
    name: str = 'service-twilio-integration'
    version: str = '0.2.0'
    username: str
    password: str
    api_key: str
    cnt_reserved_numbers: int = 0
    is_stage: bool = False


class AlertsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='../.env', env_prefix='alerts_', extra='ignore')
    service_address: str
    channel_id: int
    service_api_key: str


class TwilioCredentials(BaseSettings):
    model_config = SettingsConfigDict(env_file='../.env', env_prefix='twilio_', extra='ignore')
    account_sid: str
    auth_token: str
    address_sid: str
    test_account_sid: str
    test_auth_token: str


app_settings = AppSettings()
alerts_settings = AlertsSettings()
twilio_credentials = TwilioCredentials()
