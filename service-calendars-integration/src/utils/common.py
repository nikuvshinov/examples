import logging
from datetime import datetime as dt
from datetime import timedelta as td
from os import getenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('common-loger')


def get_env(key: str, default=None, to_log: bool = True):
    value = getenv(key, default)
    if value == default:
        logger.info(f'{key} set as default value: {value}')
    else:
        append_log = ''
        if to_log:
            append_log = f': {value}'
        logger.info(f'{key} set as value {append_log}')
    return value


class EnvVariable:

    def _get_env(self, key: str):
        return get_env(key, self._default_value, self._to_log)

    def __init__(self, default=None, to_log: bool = True):
        self._default_value = default
        self._to_log = to_log

    def __set_name__(self, owner, name):
        self._key = name
        self._value = self._get_env(self._key)

    def __get__(self, instance, owner):
        return self._value


def busy_slots_list(start: dt, end: dt, slot_duration: int):
    if slot_duration > 60:
        events_cnt_in_hour = 1
    else:
        events_cnt_in_hour = 60 // slot_duration

    if events_cnt_in_hour == 1:
        start = start.replace(minute=0, second=0, microsecond=0)
        if end != end.replace(minute=0, second=0, microsecond=0):
            end = end.replace(hour=end.hour + 1, minute=0, second=0, microsecond=0)
    else:
        c_start = start.replace(minute=0, second=0, microsecond=0)
        n_start = c_start + td(minutes=slot_duration)
        for i in range(events_cnt_in_hour):
            if c_start <= start < n_start:
                start = c_start
                break
            c_start += td(minutes=slot_duration)
            n_start += td(minutes=slot_duration)
        else:
            start = start.replace(hour=start.hour + 1, minute=0, second=0, microsecond=0)

        c_end = end.replace(minute=0, second=0, microsecond=0)
        n_end = c_end + td(minutes=slot_duration)
        for i in range(events_cnt_in_hour):
            if c_end < end <= n_end:
                end = n_end
                break
            c_end += td(minutes=slot_duration)
            n_end += td(minutes=slot_duration)

    slots = []
    slot = start
    while slot < end:
        if slot.minute % slot_duration != 0:
            slot = slot.replace(minute=0, second=0, microsecond=0)

        slots.append(slot)
        slot += td(minutes=slot_duration)

        if 60 - slot.minute < slot_duration:
            slot = slot.replace(minute=0, second=0, microsecond=0) + td(hours=1)

    return slots


def available_slots_list(start: dt, end: dt, slot_duration: int):
    if slot_duration > 60:
        events_cnt_in_hour = 1
    else:
        events_cnt_in_hour = 60 // slot_duration

    if events_cnt_in_hour == 1:
        if start != start.replace(minute=0, second=0, microsecond=0):
            start = start.replace(hour=start.hour + 1, minute=0, second=0, microsecond=0)
        end = end.replace(hour=end.hour, minute=0, second=0, microsecond=0)
    else:
        c_start = start.replace(minute=0, second=0, microsecond=0)
        for i in range(events_cnt_in_hour + 1):
            if start <= c_start:
                start = c_start
                break
            c_start += td(minutes=slot_duration)
        else:
            start = start.replace(hour=start.hour + 1, minute=0, second=0, microsecond=0)

        c_end = end.replace(minute=0, second=0, microsecond=0)
        n_end = end.replace(minute=0, second=0, microsecond=0) + td(minutes=slot_duration)
        for i in range(events_cnt_in_hour):
            if n_end > end >= c_end:
                end = c_end
                break
            c_end += td(minutes=slot_duration)
            n_end += td(minutes=slot_duration)

    slots = []
    slot = start
    while slot < end:
        if slot.minute % slot_duration != 0:
            slot = slot.replace(minute=0, second=0, microsecond=0)

        slots.append(slot)
        slot += td(minutes=slot_duration)
        if 60 - slot.minute < slot_duration:
            slot = slot.replace(minute=0, second=0, microsecond=0) + td(hours=1)

    return slots
