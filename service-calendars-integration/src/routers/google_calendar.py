from fastapi import APIRouter, Depends

from src.config import APPSettings
from src.dependencies.auth import api_key_dependency
from src.schemas.google_calendar import (
    GoogleCalendarAvailableSlotsRequest,
    GoogleCalendarEventCreateRequest,
    GoogleCalendarEventDeleteRequest,
    GoogleCalendarEventsRequest,
    GoogleCalendarRefreshTokenRequest,
    GoogleCalendarRefreshTokenResponse,
)
from src.schemas.service_response import (
    AddEventResponse,
    AvailableSlotsResponse,
    EventsResponse,
    ServiceResponse,
)
from src.services.google_calendar import GoogleCalendar

router = APIRouter(prefix="/google-calendar",
                   tags=["google-calendar"],
                   dependencies=[Depends(api_key_dependency)]
                   )


@router.post('/refresh_token', response_model=GoogleCalendarRefreshTokenResponse)
async def refresh_token(body: GoogleCalendarRefreshTokenRequest):
    """Refresh google access token by refresh token.
    If OK return 200."""
    access_token = GoogleCalendar().refresh_token(body)
    return GoogleCalendarRefreshTokenResponse(access_token=access_token)


@router.post('/available-slots', response_model=AvailableSlotsResponse)
async def get_available_slots(body: GoogleCalendarAvailableSlotsRequest):
    """Return list of available slots.
    Timezones of response corresponds to timezone of request.
    If OK return 200."""
    available_slots = GoogleCalendar().get_available_slots(body)
    return AvailableSlotsResponse(data=available_slots)


@router.post('/event', response_model=AddEventResponse)
async def add_event(body: GoogleCalendarEventCreateRequest):
    """Add new event to user calendar.
    If OK return 200."""
    new_event = GoogleCalendar().add_event(body)
    return AddEventResponse(data=new_event)


@router.delete('/event', response_model=ServiceResponse)
async def delete_event(body: GoogleCalendarEventDeleteRequest):
    """Delete event from user calendar by id.
    If OK return 200.
    """
    GoogleCalendar().delete_event(body)
    return ServiceResponse()


@router.post('/events', response_model=EventsResponse)
async def get_events(body: GoogleCalendarEventsRequest):
    """Return list of events.
    Timezones of response corresponds to timezone of request.
    If OK return 200."""
    events = await GoogleCalendar().get_events(body)
    return EventsResponse(data=events)

if APPSettings.DEBUG_MODE:
    @router.post('/busy-slots', response_model=AvailableSlotsResponse)
    async def get_busy_slots(body: GoogleCalendarAvailableSlotsRequest):
        """Return list of available slots.
        Timezones of response corresponds to timezone of request.
        If OK return 200."""
        busy_slots = GoogleCalendar()._get_busy_slots(body)
        return AvailableSlotsResponse(data=busy_slots)
