import typing as t


class BaseTwilioIntegrationException(Exception):
    pass


class NotAvailablePhoneNumbers(BaseTwilioIntegrationException):
    def __init__(self,
                 country_code: t.Literal['US', 'CA', 'GB'] = None,
                 area_code: int = None,
                 ):
        self.country_code = country_code
        self.area_code = area_code
        self.error_msg = f'Not available phone numbers! country_code={self.country_code} area_code={self.area_code}'

    def __str__(self):
        return self.error_msg
