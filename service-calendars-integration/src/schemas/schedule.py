import typing as t
from datetime import time

from pydantic import BaseModel, Field, PositiveInt, model_validator


class TimeInterval(BaseModel):
    start: time = Field(description='Start time (HH:mm)',
                        examples=[time.fromisoformat('09:00')])

    end: time | PositiveInt = Field(description='End time (HH:mm)',
                                    examples=[time.fromisoformat('17:00')]
                                    )

    def __eq__(self, other: 'TimeInterval'):
        return self.start == other.start and self.end == other.end

    @model_validator(mode='after')
    def check_correct_timings(self):
        if self.start >= self.end:
            raise ValueError('End time must be later start time!')

        return self


class Schedule(BaseModel):
    """
    Model for schedule. There are three types of rules: applicable
     - to the entire week;
     - to types of days of the week;
     - to a specific day of the week.
    The priority of applying rules from a specific day to every day.
    For example: TODO
    """
    everyday: TimeInterval | None = Field(default=None,
                                          exclude=True)
    weekdays: TimeInterval | None = Field(default=None,
                                          exclude=True)
    weekends: TimeInterval | None = Field(default=None,
                                          exclude=True)
    Mon: TimeInterval | None = None
    Tue: TimeInterval | None = None
    Wed: TimeInterval | None = None
    Thu: TimeInterval | None = None
    Fri: TimeInterval | None = None
    Sat: TimeInterval | None = None
    Sun: TimeInterval | None = None

    def __eq__(self, other: 'Schedule'):
        everyday_alias = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for alias in everyday_alias:
            if getattr(self, alias) != getattr(other, alias):
                return False
        return True

    def all_schedule(self, first_day: t.Literal['Mon', 'Sun'] = 'Mon'):
        six_day_ordered = [self.Mon, self.Tue, self.Wed, self.Thu, self.Fri, self.Sat]
        if first_day == 'Mon':
            return six_day_ordered + [self.Sun]
        elif first_day == 'Sun':
            return [self.Sun] + six_day_ordered

    @model_validator(mode='after')
    def init_schedule(self):
        weekdays_alias = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        weekends_alias = ['Sat', 'Sun']
        everyday_alias = weekdays_alias + weekends_alias

        def init_days_category(days_category: TimeInterval, aliases: list[str]):
            if days_category:
                for alias in aliases:
                    if not getattr(self, alias):
                        setattr(self, alias, days_category)

        init_days_category(self.weekdays, weekdays_alias)
        init_days_category(self.weekends, weekends_alias)
        init_days_category(self.everyday, everyday_alias)

        if not any([self.Mon, self.Tue, self.Wed, self.Thu, self.Fri, self.Sat, self.Sun]):
            raise ValueError("Schedule is empty!")

        return self
