from fastapi import APIRouter, Depends

from src.dependencies.auth import api_key_dependency
from src.schemas.calcom import (
    CalcomAvailableSlotsRequest,
    CalcomEventCreateRequest,
    CalcomEventDeleteRequest,
    CalcomEventsRequest,
)
from src.schemas.service_response import (
    AddEventResponse,
    AvailableSlotsResponse,
    EventsResponse,
    ServiceResponse,
)
from src.services.calcom import Calcom

router = APIRouter(prefix="/cal-com",
                   tags=["cal-com"],
                   dependencies=[Depends(api_key_dependency)]
                   )


@router.post('/available-slots', response_model=AvailableSlotsResponse)
async def get_available_slots(body: CalcomAvailableSlotsRequest):
    """Return list of available slots.
    Timezones of response corresponds to timezone of request.
    If OK return 200."""
    available_slots = await Calcom().get_available_slots(body)
    return AvailableSlotsResponse(data=available_slots)


@router.post('/event', response_model=AddEventResponse)
async def add_event(body: CalcomEventCreateRequest):
    """Add new event to user calendar.
    If OK return 200."""
    new_event = await Calcom().add_event(body)
    return AddEventResponse(data=new_event)


@router.delete('/event', response_model=ServiceResponse)
async def delete_event(body: CalcomEventDeleteRequest):
    """Delete event from user calendar by id.
    If OK return 200.
    """
    await Calcom().delete_event(body)
    return ServiceResponse()


@ router.post('/events', response_model=EventsResponse)
async def get_events(body: CalcomEventsRequest):
    """Return list of events.
    Timezones of response corresponds to timezone of request.
    If OK return 200."""
    events = await Calcom().get_events(body)
    return EventsResponse(data=events)
