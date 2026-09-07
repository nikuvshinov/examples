import typing as t

from pydantic import BaseModel

from src.schemas.event import Event
from src.schemas.slots_info import SlotsInfo


class ServiceResponse(BaseModel):
    data: t.Any = None
    status: t.Literal['success', 'failure'] = 'success'
    msg: str = ''
    traceback: list[str] = []


class AvailableSlotsResponse(ServiceResponse):
    data: list[SlotsInfo]


class AddEventResponse(ServiceResponse):
    data: Event


class EventsResponse(ServiceResponse):
    data: list[Event]
