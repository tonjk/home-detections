import os
import logging
import requests

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Reuse a single TCP connection pool for Telegram API calls
_session = requests.Session()


def telegram_notification(message: str, image_path: str) -> None:
    """Send a photo with caption to Telegram using a persistent HTTP session."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

    try:
        with open(image_path, "rb") as photo_file:
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": message,
                "parse_mode": "Markdown",
            }
            files = {"photo": photo_file}
            response = _session.post(url, data=payload, files=files, timeout=15)

        if response.status_code == 200:
            logger.info("Telegram notification sent successfully.")
        else:
            logger.error(
                f"Telegram notification failed. Status: {response.status_code}, "
                f"Body: {response.text}"
            )
    except Exception as e:
        logger.error(f"Error sending Telegram notification: {e}")
