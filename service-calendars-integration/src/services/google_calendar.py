import logging
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from src.config import GoogleAppCredentials
from src.exceptions import EventNotCreated, EventNotDeleted
from src.schemas.event import Event
from src.schemas.google_calendar import (
    GoogleCalendarAvailableSlotsRequest,
    GoogleCalendarEventCreateRequest,
    GoogleCalendarEventDeleteRequest,
    GoogleCalendarEventsRequest,
    GoogleCalendarRefreshTokenRequest,
)
from src.schemas.schedule import TimeInterval
from src.schemas.slots_info import SlotsInfo
from src.services.base_calendar import BaseCalendar
from src.utils.common import available_slots_list, busy_slots_list

logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.WARNING)


class GoogleCalendar(BaseCalendar):
    # TODO add async API (https://github.com/omarryhan/aiogoogle)
    # TODO replace sync to async API

    def __init__(self):
        self.__calendar_service = None

    def _calendar_service(self, token: str):
        if not self.__calendar_service:
            if token == 'test':
                SCOPES = ["https://www.googleapis.com/auth/calendar", ]
                creds = Credentials.from_authorized_user_file(
                    "token.json", SCOPES)
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                token = creds.token
            self.__calendar_service = build(
                "calendar", "v3", credentials=Credentials(token))
        return self.__calendar_service

    def refresh_token(self, request: GoogleCalendarRefreshTokenRequest) -> str:
        creds = Credentials(token='', 
                            refresh_token=request.refresh_token,
                            token_uri='https://oauth2.googleapis.com/token',
                            client_id=GoogleAppCredentials.GOOGLE_CLIENT_ID,
                            client_secret=GoogleAppCredentials.GOOGLE_CLIENT_SECRET,
                            )
        creds.refresh(Request())
        return creds.token
        
    
    def add_event(self, request: GoogleCalendarEventCreateRequest) -> Event:
        print(f'{request=}')
        calendar_service = self._calendar_service(request.token)
        
        available_slots = self.get_available_slots(GoogleCalendarAvailableSlotsRequest(dates=[request.datetime.date()],
                                                                                       duration=request.duration,
                                                                                       schedule=request.schedule,
                                                                                       tz_offset=request.tz_offset,
                                                                                       token=request.token,
                                                                                       calendar_id=request.calendar_id,
                                                                                       client_phone=request.client_phone,
                                                                                       subscriber_phone=request.subscriber_phone
                                                                                       ))
        
        if not (request.datetime.time() in available_slots[0].raw_slots):
            print(f'{available_slots[0].raw_slots=}')
            raise EventNotCreated("Event time is busy!")
        
        start = request.datetime.replace(
            tzinfo=tz(td(hours=request.tz_offset))).isoformat()
        end = (request.datetime + td(minutes=request.duration)).replace(
            tzinfo=tz(td(hours=request.tz_offset))).isoformat()

        body = {
            "summary": request.name,
            "attendees": [
                {"email": request.client_email},
                {"email": request.subscriber_email},
            ],
            "start": {
                "dateTime": start
            },
            "description": request.summary,
            "end": {
                "dateTime": end
            },
        }
        result = calendar_service.events().insert(calendarId=request.calendar_id,
                                                  body=body).execute()

        if not result.get("id"):
            raise EventNotCreated(result)

        return Event(datetime=result["start"]["dateTime"],
                     duration=request.duration,
                     tz_offset=request.tz_offset,
                     id=result["id"],
                     name=result["summary"],
                     client_email=request.client_email,
                     subscriber_email=request.subscriber_email,
                     client_phone=request.client_phone,
                     subscriber_phone=request.subscriber_phone,
                     summary=result["description"],
                     )

    def delete_event(self, request: GoogleCalendarEventDeleteRequest) -> None:
        calendar_service = self._calendar_service(request.token)
        result = calendar_service.events().delete(calendarId=request.calendar_id,
                                                  eventId=request.id).execute()
        if result:
            raise EventNotDeleted(result)

    def get_available_slots(self, request: GoogleCalendarAvailableSlotsRequest) -> list[SlotsInfo]:
        busy_slots = self._get_busy_slots(request)

        now = dt.now().astimezone(tz(td(hours=request.tz_offset))).replace(tzinfo=None)
        available_slots = {busy_slot.raw_date: [] for busy_slot in busy_slots}
        if schedule := request.schedule:
            for busy_slot in busy_slots:
                week_day = busy_slot.raw_date.strftime('%a')
                if day_schedule := getattr(schedule, week_day):
                    day_schedule: TimeInterval
                    day_start = dt.combine(
                        busy_slot.raw_date, day_schedule.start)
                    day_end = dt.combine(busy_slot.raw_date, day_schedule.end)
                    day_start = max(day_start, now)
                    day_available_slots = available_slots_list(
                        day_start, day_end, request.duration)
                    day_available_slots = list(
                        map(lambda datetime: datetime.time(), day_available_slots))
                    available_slots[busy_slot.raw_date] = list(
                        set(day_available_slots) - set(busy_slot.raw_slots))

        available_slots_info = [SlotsInfo(
            raw_date=date, raw_slots=slots) for date, slots in available_slots.items()]

        return available_slots_info

    async def get_events(self, request: GoogleCalendarEventsRequest) -> list[Event]:
        calendar_service = self._calendar_service(request.token)

        page_token = None
        events = []
        while True:
            response = calendar_service.events().list(
                calendarId=request.calendar_id,
                pageToken=page_token,
                maxResults=2500,
                eventTypes="default",
                timeMin=dt.now().astimezone(tz(td(hours=request.tz_offset))).isoformat(),
                singleEvents=True,
                orderBy="startTime").execute()
            events.extend(response['items'])
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        
        res_events = []
        for event in events:

            datetime = dt.fromisoformat(event['start']['dateTime']).astimezone(
                tz(td(hours=request.tz_offset))).isoformat()

            duration = (dt.fromisoformat(event['end']['dateTime']) -
                        dt.fromisoformat(event['start']['dateTime'])).total_seconds() / 60
            duration = int(duration)
            try:
                client_email = next(filter(lambda attendee: attendee.get(
                    'organizer') and attendee.get('email'), event['attendees']))["email"]
            except StopIteration:
                client_email = ''

            try:
                subscriber_email = next(filter(lambda attendee: attendee.get(
                    'email') and attendee.get('email') != client_email, event['attendees']))["email"]
            except StopIteration:
                subscriber_email = ''

            res_events.append(Event(id=event['id'],
                                    datetime=datetime,
                                    duration=duration,
                                    tz_offset=request.tz_offset,
                                    name=event['summary'],
                                    summary=event['description'],
                                    client_email=client_email,
                                    subscriber_email=subscriber_email
                                    ))

        return res_events

    def _get_busy_slots(self, request: GoogleCalendarAvailableSlotsRequest) -> list[SlotsInfo]:
        calendar_service = self._calendar_service(request.token)
        start_time = dt.combine(min(request.dates), dt.min.time()).replace(
            tzinfo=tz(td(hours=request.tz_offset)))
        end_time = dt.combine(max(request.dates), dt.max.time()).replace(
            tzinfo=tz(td(hours=request.tz_offset)))

        body = {
            "items": [{"id": request.calendar_id}],
            "timeMin": start_time.isoformat(),
            "timeMax": end_time.isoformat(),
            "timeZone": str(tz(td(hours=request.tz_offset))),
        }

        response = calendar_service.freebusy().query(body=body).execute()
        busy_list: list[dict[str, str]
                        ] = response["calendars"][request.calendar_id]["busy"]

        all_slots = []

        for busy_time in busy_list:
            all_slots.extend(busy_slots_list(dt.fromisoformat(busy_time['start'].replace('Z', '+00:00')), dt.fromisoformat(busy_time["end"].replace('Z', '+00:00')),
                                             request.duration))

        all_slots_info = {date: [] for date in request.dates}

        for slot in set(all_slots):
            if slot.date() in request.dates:
                all_slots_info[slot.date()].append(slot.time())

        busy_slots = []
        for date, slots in all_slots_info.items():
            busy_slots.append(SlotsInfo(raw_date=date, raw_slots=slots))

        return busy_slots
