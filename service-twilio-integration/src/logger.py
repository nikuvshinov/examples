import logging

from config import app_settings

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(app_settings.name)
