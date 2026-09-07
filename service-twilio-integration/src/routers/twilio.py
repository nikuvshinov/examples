from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_cache.decorator import cache
from pydantic import PositiveInt

from dependencies.auth import api_key_dependency
from schemas.twilio_number import (
    AvailableNumberTwilioRequest,
    BuyTwilioNumberRequest,
    IncomingTwilioNumber,
    TestBuyTwilioNumberRequest,
    TestTwilioNumbers,
)
from services.twilio_service import twilio_service

router = APIRouter(prefix="/twilio",
                   tags=["twilio"],
                   dependencies=[Depends(api_key_dependency)]
                   )


@router.get('/get_balance', status_code=status.HTTP_200_OK)
async def get_balance() -> JSONResponse:
    """Check twilio account balance.
    NO NEED TO PAY.
    If OK return 200"""
    balance = await twilio_service.get_balance()
    return JSONResponse(balance)


@router.get('/my_numbers', status_code=status.HTTP_200_OK)
async def my_numbers():
    """Get list available numbers.
    NO NEED TO PAY.
    If OK return 200"""
    numbers = await twilio_service._list_my_numbers()
    return numbers


@router.get('/available_numbers', status_code=status.HTTP_200_OK)
async def available_numbers(number_criteria: AvailableNumberTwilioRequest = Depends(),
                            limit: PositiveInt = 15) -> JSONResponse:
    """Get list available numbers.
    NO NEED TO PAY.
    If OK return 200"""
    numbers = await twilio_service.list_available_numbers(number_criteria.country_code, number_criteria.area_code,
                                                           limit)

    return JSONResponse(numbers)


@router.post('/buy_number_test', status_code=status.HTTP_200_OK)
async def buy_number_test(
        number_data: TestBuyTwilioNumberRequest,
) -> IncomingTwilioNumber:
    """Buy number use test account credentials (FAKE BUY).
    Country code only 'US', area_code 500 - success pay, other - failed pay.
    NO NEED TO PAY.
    If OK return 200"""
    new_number = await twilio_service.buy_number_test(number_data.country_code,
                                                number_data.area_code,
                                                number_data.incoming_webhook_url)
    return new_number


@router.post('/buy_number',
             status_code=status.HTTP_200_OK,
             tags=['NEED TO PAY'])
async def buy_number(number_data: BuyTwilioNumberRequest) -> IncomingTwilioNumber:
    """Buy number.
    Country code only 'US', 'CA', 'GB'.
    WARNING! NEED TO PAY.
    If OK return 200"""
    new_number = await twilio_service.buy_number(number_data.country_code,
                                                  number_data.area_code,
                                                  number_data.incoming_webhook_url,
                                                  number_data.payment_mode)
    return new_number


@router.get('/test_numbers', status_code=status.HTTP_200_OK)
@cache(expire=60*60*2)
async def get_test_numbers() -> TestTwilioNumbers:
    return await twilio_service.get_test_numbers()
