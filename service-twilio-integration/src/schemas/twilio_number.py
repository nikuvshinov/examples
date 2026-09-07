import typing as t

from pydantic import BaseModel, HttpUrl, PositiveInt
from twilio.rest.api.v2010.account.incoming_phone_number import (
    IncomingPhoneNumberInstance,
)


class AvailableNumberTwilioRequest(BaseModel):
    country_code: t.Literal['US', 'CA', 'GB']
    area_code: PositiveInt | None = None


class BuyTwilioNumberRequest(AvailableNumberTwilioRequest):
    incoming_webhook_url: HttpUrl
    payment_mode: t.Literal['direct', 'reserved'] = 'reserved'


class TestBuyTwilioNumberRequest(BuyTwilioNumberRequest):
    country_code: t.Literal['US']
    area_code: PositiveInt = 500


class IncomingTwilioNumber(BaseModel):
    phone_number: str
    capabilities: dict[str, bool]
    friendly_name: str
    sid: str
    uri: str
    voice_method: str
    voice_url: HttpUrl | None
    status: str

    @classmethod
    def from_incoming_phone_number_instance(cls, incoming_phone_number_instance: IncomingPhoneNumberInstance):
        phone_number_data = {
            key: value for key, value in incoming_phone_number_instance.__dict__.items() if
            not key.startswith('_')
        }
        return cls(**phone_number_data)


TestTwilioNumbers = dict[str, IncomingTwilioNumber]
