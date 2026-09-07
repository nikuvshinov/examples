from datetime import datetime as dt
from datetime import timedelta as td

from pydantic import BaseModel, EmailStr, Field, PositiveInt

from src.schemas.schedule import Schedule


class EventCreateRequest(BaseModel):
    datetime: dt = Field(description='Start event time (YYYY-MM-DDTHH:mm:ss)',
                         examples=[(dt.utcnow() + td(days=3, hours=2)).strftime(
                             "%Y-%m-%dT%H:00")])
    duration: PositiveInt = Field(description='Event duration (minutes)',
                                  examples=[30, 60])
    tz_offset: float = Field(default=0,
                             description='Time offset for data transmitted in the request',
                             examples=[3, 2.5],
                             ge=-12, le=+14)
    name: str = Field(default='JIQ Event',
                      description='Name of event',
                      examples=["Scrum meetup"])
    client_email: EmailStr | str = Field(default='testintegrationsk@gmail.com',
                                         description="Client's email",
                                         examples=["testintegrationsk@gmail.com"])
    subscriber_email: EmailStr | str = Field(default='subscriber@jiq.com',
                                             description="Subscriber's email",
                                             examples=["subscriber@jiq.com"])

    summary: str = Field(default='JIQ Summary',
                         description='Call summary',
                         examples=['Discussion of task assessment'])
    
    schedule: Schedule | None = Field(default=None,
                                      description='Schedule of client',
                                      examples=[Schedule(everyday={"start": "09:00", "end": "17:00"})])


class EventDeleteRequest(BaseModel):
    id: str = Field(description='Event id')


class EventsRequest(BaseModel):
    tz_offset: float = Field(default=0,
                             description='Time offset for data transmitted in the request',
                             examples=[3, 2.5],
                             ge=-12, le=+14)


class Event(EventCreateRequest, EventDeleteRequest):
    pass
