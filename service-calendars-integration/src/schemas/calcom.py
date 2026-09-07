from pydantic import BaseModel, Field, computed_field, model_validator
from pydantic.json_schema import SkipJsonSchema

from src.schemas.available_slots import AvailableSlotsRequest
from src.schemas.event import EventCreateRequest, EventDeleteRequest, EventsRequest


class CalcomRequest(BaseModel):
    token: str = Field(description="Client's calcom auth data ('{username}:{api_key}:{eventTypeId}')",
                       examples=['test'])
    duration: SkipJsonSchema[None] = Field(default=None, exclude=True)
    schedule: SkipJsonSchema[None] = Field(default=None, exclude=True)
    client_email: SkipJsonSchema[None] = Field(default=None, exclude=True)
    client_phone: str = Field(default='70000000000',
                              description="Client's phone",
                              examples=["70000000000"])
    subscriber_phone: str = Field(default='79999999999',
                                  description="Subscriber's phone",
                                  examples=["79999999999"])

    @model_validator(mode='after')
    def parse_token(self):
        if self.token != 'test':
            parts = self.token.split(':')
            if len(parts) != 3:
                raise ValueError(
                    "Token must contain '{username}:{api_key}:{eventTypeId}'!")
        return self

    @computed_field(examples=['testintegrations-test'])
    @property
    def username(self) -> str:
        if self.token == 'test':
            return 'testintegrations-test'
        return self.token.split(':')[0]

    @computed_field(examples=['cal_live_d61bfb7bd4e490297bd1c8538bb3cfb5'])
    @property
    def api_key(self) -> str:
        if self.token == 'test':
            return 'cal_live_d61bfb7bd4e490297bd1c8538bb3cfb5'
        return self.token.split(':')[1]

    @computed_field(examples=[633713])
    @property
    def event_type_id(self) -> int:
        if self.token == 'test':
            return 633713
        return int(self.token.split(':')[2])


class CalcomAvailableSlotsRequest(CalcomRequest, AvailableSlotsRequest):
    pass


class CalcomEventCreateRequest(CalcomRequest, EventCreateRequest):
    pass


class CalcomEventDeleteRequest(CalcomRequest, EventDeleteRequest):
    pass


class CalcomEventsRequest(CalcomRequest, EventsRequest):
    pass
