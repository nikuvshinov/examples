from aiohttp import ClientSession, ClientTimeout

from config import alerts_settings
from logger import logger


async def send_telegram_message(message: str):
    try:
        details = ''
        async with ClientSession(alerts_settings.service_address, timeout=ClientTimeout(3), headers={'xi-api-key': alerts_settings.service_api_key}) as session:
            async with session.post('/send_message', json={'text': message, 'channel': alerts_settings.channel_id, }) as response:
                if not response.ok:
                    details = await response.json()
                    raise Exception()
    except:
        logger.error(f'Не могу отправить алерт! to: {alerts_settings.channel_id} text: {message} {details=}')
                    