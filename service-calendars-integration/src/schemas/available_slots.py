from datetime import date
from datetime import timedelta as td

from pydantic import BaseModel, Field, PositiveInt

from src.schemas.schedule import Schedule


class AvailableSlotsRequest(BaseModel):
    dates: list[date] = Field(description='Dates for which to return available slots',
                              examples=[[date.today(),
                                         date.today() + td(days=1),
                                         date.today() + td(days=3),
                                         ]])
    duration: PositiveInt = Field(description='Slot duration (minutes)',
                                  examples=[60, 30])
    schedule: Schedule | None = Field(default=None,
                                      description='Schedule of client',
                                      examples=[Schedule(everyday={"start": "09:00", "end": "17:00"})])
    tz_offset: float = Field(default=0,
                             description='Time offset for data transmitted in the request',
                             examples=[3, 2.5],
                             ge=-12, le=+14)
