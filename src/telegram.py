"""Send digest to Telegram."""
import requests
from .config import TelegramConfig

MAX_MSG_LEN = 4096


def send(text: str, cfg: TelegramConfig) -> bool:
    """Send message to Telegram, splitting if needed."""
    chunks = [text[i : i + MAX_MSG_LEN] for i in range(0, len(text), MAX_MSG_LEN)]

    for chunk in chunks:
        resp = requests.post(
            f"https://api.telegram.org/bot{cfg.bot_token}/sendMessage",
            json={"chat_id": cfg.chat_id, "text": chunk},
            timeout=15,
        )
        if not resp.ok:
            print(f"Telegram error: {resp.text}")
            return False
    return True
