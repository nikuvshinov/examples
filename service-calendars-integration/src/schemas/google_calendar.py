from pydantic import BaseModel, Field

from src.schemas.available_slots import AvailableSlotsRequest
from src.schemas.event import EventCreateRequest, EventDeleteRequest, EventsRequest


class GoogleCalendarRefreshTokenRequest(BaseModel):
    refresh_token: str = Field(description="Client's google refresh token",
                       examples=['test'])
    

class GoogleCalendarRefreshTokenResponse(BaseModel):
    access_token: str = Field(description="Client's google access token",
                       examples=['test'])


class GoogleCalendarRequest(BaseModel):
    token: str = Field(description="Client's google access token",
                       examples=['test'])
    calendar_id: str = Field(default='primary',
                             description="Client's google calendar id")
    client_phone: str = Field(default='70000000000',
                              description="Client's phone",
                              examples=["70000000000"])
    subscriber_phone: str = Field(default='79999999999',
                                  description="Subscriber's phone",
                                  examples=["79999999999"])


class GoogleCalendarAvailableSlotsRequest(GoogleCalendarRequest, AvailableSlotsRequest):
    pass


class GoogleCalendarEventCreateRequest(GoogleCalendarRequest, EventCreateRequest):
    pass


class GoogleCalendarEventDeleteRequest(GoogleCalendarRequest, EventDeleteRequest):
    pass


class GoogleCalendarEventsRequest(GoogleCalendarRequest, EventsRequest):
    pass
