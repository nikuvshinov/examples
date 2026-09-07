from datetime import date, time

from pydantic import BaseModel, Field, computed_field


class PrettyDate(BaseModel):
    raw_date: date = Field(exclude=True)

    @computed_field(examples=['Wednesday 13. March 2024'])
    @property
    def date(self) -> str:
        return self.raw_date.strftime('%A %-d. %B %Y')


class SlotsInfo(PrettyDate):
    raw_slots: set[time] = Field(default=[],
                                 examples=[[time.fromisoformat('13:00'), time.fromisoformat('15:00')]],
                                 exclude=True)

    @computed_field(examples=[[time.fromisoformat('13:00'), time.fromisoformat('15:00')]])
    @property
    def slots(self) -> list[str]:
        return sorted(set([slot.strftime("%H:%M") for slot in self.raw_slots]))
