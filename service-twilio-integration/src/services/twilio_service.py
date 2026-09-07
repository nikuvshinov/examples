import asyncio
import time
import typing as t

from pydantic import HttpUrl, PositiveInt
from twilio.base.exceptions import TwilioRestException
from twilio.http.async_http_client import AsyncTwilioHttpClient
from twilio.rest import Client

from config import app_settings, twilio_credentials
from exceptions import NotAvailablePhoneNumbers
from logger import logger
from schemas.twilio_number import IncomingTwilioNumber
from utils.telegram import send_telegram_message


class TwilioService:
    NOT_AVAILABLE_NUMBER_CODE = 21452
    NOT_AVAILABLE_NUMBER = 21422

    def __init__(self):
        self._client = Client(twilio_credentials.account_sid,
                              twilio_credentials.auth_token,
                              http_client=AsyncTwilioHttpClient(),
                              )
        self._test_client = Client(twilio_credentials.test_account_sid,
                                   twilio_credentials.test_auth_token,
                                   http_client=AsyncTwilioHttpClient(),
                                   )
        
        if app_settings.cnt_reserved_numbers > 0:
            print(app_settings.cnt_reserved_numbers)
            
            self._reserved_numbers = {
                'US': asyncio.Queue(),
                'CA': asyncio.Queue(),
            }
            self._task_reserve_numbers = asyncio.get_event_loop().create_task(self._reserve_numbers())
        
    async def get_balance(self):
        res = await self._client.balance.fetch_async()
        balance_data = {key: value for key, value in res.__dict__.items() if
                        not key.startswith('_')}
        return balance_data

    async def list_my_numbers(self):
        my_numbers_list = await self._list_my_numbers()
        return [number_obj.phone_number for number_obj in my_numbers_list]

    async def list_available_numbers(self,
                                     country_code: t.Literal['US', 'CA', 'GB'],
                                     area_code: PositiveInt | None = None,
                                     limit: PositiveInt = 15) -> list[str]:
        request_params = {'voice_enabled': True, 'limit': limit}
        if area_code:
            request_params['area_code'] = area_code
        
        available_numbers_list = await self._client.available_phone_numbers(country_code).local.list_async(
            **request_params
            )
        if not available_numbers_list:
            err = NotAvailablePhoneNumbers(country_code, area_code)
            logger.error(err.error_msg)
            raise err

        return [number_obj.phone_number for number_obj in available_numbers_list]

    async def buy_number(self,
                         country_code: t.Literal['US', 'CA', 'GB'],
                         area_code: PositiveInt | None = None,
                         incoming_webhook_url: HttpUrl = None,
                         payment_mode: t.Literal['direct', 'reserved'] = 'reserved',
                         ) -> IncomingTwilioNumber:
        try:
            if payment_mode == 'reserved' and app_settings.cnt_reserved_numbers > 0:
                number = await self._get_reserved_number(country_code)
                new_friendly_name = f'in_use {country_code}'

                await self._client.incoming_phone_numbers.get(number.sid).update_async(
                    friendly_name=new_friendly_name,
                    voice_url=str(incoming_webhook_url),
                    voice_method='GET',
                    )
                
                number.friendly_name = new_friendly_name
                number.voice_url = incoming_webhook_url
                number.voice_method = 'GET'
                
                return number
        except:
            pass
        return await self._buy_number(country_code,
                                      area_code,
                                      incoming_webhook_url,
                                      )

    async def buy_number_test(self,
                        country_code: t.Literal['US'],
                        area_code: PositiveInt,
                        incoming_webhook_url: HttpUrl,
                        ) -> IncomingTwilioNumber:
        try:
            incoming_phone_number = await self._test_client.incoming_phone_numbers.create_async(area_code=area_code,
                                                                                    voice_url=str(incoming_webhook_url),
                                                                                    voice_method='GET')
            return IncomingTwilioNumber.from_incoming_phone_number_instance(incoming_phone_number)
        except TwilioRestException as exc:
            if exc.code == self.NOT_AVAILABLE_NUMBER_CODE:
                err = NotAvailablePhoneNumbers(country_code, area_code)
                logger.error(err.error_msg)
                raise err

            else:
                raise

    async def get_test_numbers(self):
        my_numbers_list = await self._list_my_numbers()

        test_numbers = {}

        stage_prefix = '' if not app_settings.is_stage else 'stage_'
        for number in my_numbers_list:
            if number.friendly_name.startswith(f'{stage_prefix}TEST_NUMBER'):
                region = number.friendly_name.split()[1]
                if region in test_numbers:
                    logger.warning(f'Несколько тестовых номеров на регион: {region=} {number=}')
                    continue
                test_numbers[region] = number

        return test_numbers
    
    async def _reserve_numbers(self):
        while True:
            try:
                reserve_numbers = await self._list_my_numbers(is_reserved=True)
                break
            except Exception as err:
                error = 'Не могу получить список резервированных номеров с twilio!'
                logger.error(error + f' {type(err)} {err}')
                asyncio.create_task(send_telegram_message(error))
                await asyncio.sleep(60)

        for number in reserve_numbers:
            _, country_code = number.friendly_name.split()
            logger.info(f'Резервный номер {country_code}: {number.phone_number}')
            self._reserved_numbers[country_code].put_nowait(number)
        
        _alert_delay = 120
        _last_alert_time = time.time() - _alert_delay
        while True:
            for country_code, numbers in self._reserved_numbers.items():
                try:
                    while True:
                        if numbers.qsize() < app_settings.cnt_reserved_numbers:
                            number = await self._reserve_buy_number(country_code)
                            numbers.put_nowait(number)
                            logger.info(f'Новый резервный номер {country_code}: {number.phone_number}')
                        else:
                            break
                except Exception as exc:
                    if time.time() - _alert_delay >= _last_alert_time:
                        _last_alert_time = time.time()
                        error = f'Не могу купить (зарезервировать) номер {country_code=} {exc=}'
                        asyncio.create_task(send_telegram_message(error))
            await asyncio.sleep(3)

    async def _list_my_numbers(self, is_reserved: bool = False) -> list[IncomingTwilioNumber]:
        my_numbers = await self._client.incoming_phone_numbers.list_async()
        stage_prefix = '' if not app_settings.is_stage else 'stage_'
        if is_reserved:
            reserved_numbers = []
            for number in my_numbers:
                if number.friendly_name.startswith(f'{stage_prefix}RESERVED'):
                    reserved_numbers.append(number)
            my_numbers = reserved_numbers
    
        return [IncomingTwilioNumber.from_incoming_phone_number_instance(number) for number in my_numbers]

    async def _buy_number(self,
                         country_code: t.Literal['US', 'CA', 'GB'],
                         area_code: PositiveInt | None = None,
                         incoming_webhook_url: HttpUrl | None = None,
                         friendly_name: str | None = None,
                         ) -> IncomingTwilioNumber:
        try:
            available_numbers_list = await self.list_available_numbers(
                country_code, area_code, limit=1)
            available_number = available_numbers_list[-1]

            request_params = {
                'phone_number': available_number, 
                'voice_url': str(incoming_webhook_url),
                'voice_method': 'GET',
                'address_sid': twilio_credentials.address_sid,
                }
            if friendly_name:
                request_params['friendly_name'] = friendly_name

            incoming_phone_number = await self._client.incoming_phone_numbers.create_async(**request_params)
            
            return IncomingTwilioNumber.from_incoming_phone_number_instance(incoming_phone_number)

        except TwilioRestException as exc:
            if exc.code == self.NOT_AVAILABLE_NUMBER_CODE:
                err = NotAvailablePhoneNumbers(country_code, area_code)
                logger.error(err.error_msg)
                asyncio.create_task(send_telegram_message(f'Не могу купить номер {country_code=} {area_code=} !\n{err.error_msg}')) 
                raise err
            elif exc.code == self.NOT_AVAILABLE_NUMBER:
                return await self.buy_number(country_code, area_code, incoming_webhook_url)

            else:
                await send_telegram_message(f'Не могу купить номер {country_code=} {area_code=} !\n{exc}')
                raise
        except Exception as exc:
            await send_telegram_message(f'Не могу купить номер {country_code=} {area_code=} !\n{exc}')
            raise

    async def  _get_reserved_number(self, country_code: t.Literal['US', 'CA', 'GB']) -> IncomingTwilioNumber:
        try:
            number = self._reserved_numbers[country_code].get_nowait()
            return number
        except asyncio.QueueEmpty:
            error = f'Нет номера в резерве {country_code=}'
            logger.error(error)
            asyncio.create_task(send_telegram_message(error))
            raise Exception(error)
              
    async def _reserve_buy_number(self,
                         country_code: t.Literal['US', 'CA', 'GB'],
                         area_code: PositiveInt | None = None,
                         ) -> IncomingTwilioNumber:
        stage_prefix = '' if not app_settings.is_stage else 'stage_'
        number = await self._buy_number(
            country_code,
            area_code,
            'https://example.com/',
            f'{stage_prefix}RESERVED {country_code}',
        )
        return number

twilio_service = TwilioService()
