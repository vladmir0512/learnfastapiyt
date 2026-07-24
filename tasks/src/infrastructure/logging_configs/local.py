import logging
from logging.handlers import TimedRotatingFileHandler
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=2, encoding="utf-8"
)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("fastapi-app")
logger.setLevel(logging.INFO)
logger.addHandler(handler)