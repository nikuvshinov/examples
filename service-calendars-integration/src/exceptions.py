class BaseCalendarsIntegrationsException(Exception):
    pass


class CalendarOptionsNotFound(BaseCalendarsIntegrationsException):
    def __init__(self, _id: str):
        self.id = _id
        super().__init__()

    def __str__(self):
        return f'{self.__class__.__name__}({self.id=})'


class IncorrectCalendarOptions(BaseCalendarsIntegrationsException):
    def __init__(self, _id: str):
        self.id = _id
        super().__init__()

    def __str__(self):
        return f'{self.__class__.__name__}({self.id=})'


class EventNotCreated(BaseCalendarsIntegrationsException):
    def __init__(self, details: str | dict):
        self.details = details
        super().__init__()

    def __str__(self):
        return f'{self.__class__.__name__} response body:\n{self.details}'


class EventNotDeleted(BaseCalendarsIntegrationsException):
    def __init__(self, details: str | dict):
        self.details = details
        super().__init__()

    def __str__(self):
        return f'{self.__class__.__name__} response body:\n{self.details}'
