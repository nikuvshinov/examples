from abc import ABC, ABCMeta, abstractmethod

from src.schemas.available_slots import AvailableSlotsRequest
from src.schemas.event import (
    Event,
    EventCreateRequest,
    EventDeleteRequest,
    EventsRequest,
)
from src.schemas.slots_info import SlotsInfo


class BaseCalendar(ABC, metaclass=ABCMeta):

    @abstractmethod
    def add_event(self, request: EventCreateRequest) -> Event:
        pass

    @abstractmethod
    def delete_event(self, request: EventDeleteRequest) -> None:
        pass

    @abstractmethod
    def get_available_slots(self, request: AvailableSlotsRequest) -> list[SlotsInfo]:
        pass

    @abstractmethod
    def get_events(self, request: EventsRequest) -> list[Event]:
        pass
