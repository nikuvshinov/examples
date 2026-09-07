from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz

import aiohttp

from src.exceptions import EventNotCreated, EventNotDeleted
from src.schemas.calcom import (
    CalcomAvailableSlotsRequest,
    CalcomEventCreateRequest,
    CalcomEventDeleteRequest,
    CalcomEventsRequest,
    CalcomRequest,
)
from src.schemas.event import Event
from src.schemas.slots_info import SlotsInfo
from src.services.base_calendar import BaseCalendar
from src.utils.common import available_slots_list


class Calcom(BaseCalendar):

    async def add_event(self, request: CalcomEventCreateRequest) -> Event:
        start = request.datetime.replace(
            tzinfo=tz(td(hours=request.tz_offset))).astimezone(tz(td(hours=0)))

        body = {
            "eventTypeId": request.event_type_id,
            "start": start.isoformat(),
            "timeZone": 'UTC',
            "language": "en",
            "status": "PENDING",
            "responses": {
                "name": request.subscriber_email,
                "email": request.subscriber_email,
                "notes": request.summary,
                "metadata": {}
            },
            "metadata": {"name": request.name}
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f'https://api.cal.com/v1/bookings?apiKey={request.api_key}', json=body) as resp:
                if resp.ok:
                    result = await resp.json()
                    duration = self._dt_from_calcom(result["endTime"], request.tz_offset) - self._dt_from_calcom(
                        result["startTime"], request.tz_offset)
                    duration = duration.total_seconds() // 60
                    return Event(datetime=self._dt_from_calcom(result["startTime"], request.tz_offset),
                                 duration=duration,
                                 tz_offset=request.tz_offset,
                                 id=str(result["id"]),
                                 name=result["title"],
                                 client_email=result["userPrimaryEmail"],
                                 subscriber_email=result["responses"]["email"],
                                 client_phone=request.client_phone,
                                 subscriber_phone=request.subscriber_phone,
                                 summary=result["responses"]["notes"],
                                 )
                else:
                    raise EventNotCreated(await resp.text())

    async def delete_event(self, request: CalcomEventDeleteRequest) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.delete(f'https://api.cal.com/v1/bookings/{request.id}/cancel?apiKey={request.api_key}') as resp:
                if not resp.ok:
                    raise EventNotDeleted(await resp.text())

    async def get_available_slots(self, request: CalcomAvailableSlotsRequest) -> list[SlotsInfo]:

        start_time = min(request.dates)
        end_time = max(request.dates) + td(days=1)

        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.cal.com/v1/availability?'
                                   f'username={request.username}&'
                                   f'dateFrom={start_time}&'
                                   f'dateTo={end_time}&'
                                   f'apiKey={request.api_key}') as resp:

                if resp.ok:
                    data = await resp.json()
                    duration = await self._get_event_duration(request)

                    available_slots = {date: [] for date in request.dates}

                    for date_range in data["dateRanges"]:
                        date = self._dt_from_calcom(
                            date_range["start"], request.tz_offset).date()
                        if date not in available_slots:
                            continue
                        day_available_slots = available_slots_list(self._dt_from_calcom(date_range["start"], request.tz_offset),
                                                                   self._dt_from_calcom(
                            date_range["end"], request.tz_offset),
                            duration)

                        day_available_slots = list(
                            map(lambda datetime: datetime.time(), day_available_slots))
                        available_slots[date].extend(day_available_slots)

                    available_slots_info = [SlotsInfo(raw_date=date, raw_slots=slots) for date, slots in
                                            available_slots.items()]

                    return available_slots_info

                else:
                    raise Exception(await resp.text())

    async def get_events(self, request: CalcomEventsRequest) -> list[Event]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.cal.com/v1/bookings?'
                                   f'filter=upcoming&'
                                   f'apiKey={request.api_key}') as resp:
                data = await resp.json()

        events = data.get('bookings', [])

        res_events = []
        for event in events:

            datetime = self._dt_from_calcom(event['startTime'],
                                            request.tz_offset).isoformat()

            duration = (self._dt_from_calcom(event['endTime'],
                                             request.tz_offset) - self._dt_from_calcom(event['startTime'],
                                                                                       request.tz_offset)).total_seconds() / 60

            duration = int(duration)

            client_email = event.get("user", {}).get("email", "")
            subscriber_email = event.get("attendees", [{}])[0].get("email", "")

            res_events.append(Event(id=str(event['id']),
                                    datetime=datetime,
                                    duration=duration,
                                    tz_offset=request.tz_offset,
                                    name=event['metadata']['name'],
                                    summary=event['description'],
                                    client_email=client_email,
                                    subscriber_email=subscriber_email
                                    ))

        return res_events

    async def _get_event_duration(self, request: CalcomRequest) -> int:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.cal.com/v1/event-types/{request.event_type_id}?apiKey={request.api_key}') as resp:

                if resp.ok:
                    return int((await resp.json())["event_type"]["length"])
                else:
                    raise Exception(await resp.text())

    def _dt_from_calcom(self, string: str, tz_offset: int) -> dt:
        return dt.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=tz(td(0))).astimezone(
            tz(td(hours=tz_offset)))
