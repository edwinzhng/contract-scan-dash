import json
import logging
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from telegram.bot import Bot

from app import crud
from app.database import get_db
from app.settings import settings
from app.web import post_async

bot = Bot(token=settings.telegram_bot_token)


TELEGRAM_SET_WEBHOOK_URL = "https://api.telegram.org/bot{token}/setWebhook"
VALID_COMMANDS = ["start", "sub", "unsub", "registered"]


async def set_telegram_webhook_url():
    token = settings.telegram_bot_token
    data = {"url": f"{settings.telegram_webhook_host}/webhook/{token}"}
    res = await post_async(TELEGRAM_SET_WEBHOOK_URL.format(token=token), data)
    if res.status_code == 200:
        logging.info("Successfully set Telegram webhook URL")
        return

    content = json.loads(res.content.decode("utf-8"))
    if content.get("description") == "Webhook is already set":
        return
    raise Exception("Failed to set Telegram webhook URL", content)


def send_message(chat_id: int, message: str, parse_mode: Optional[str] = "Markdown"):
    bot.send_message(
        chat_id, message, parse_mode=parse_mode, disable_web_page_preview=True
    )


def handle_commands(chat_id: int, text: str):
    command, args = _parse_command(text)
    if not command:
        send_message(chat_id, "Unrecognized command 😿")

    db = next(get_db())
    if command == "start":
        send_message(chat_id, "hello frens!")
    elif command == "sub":
        _handle_sub(db, chat_id, args)
    elif command == "unsub":
        _handle_unsub(db, chat_id, args)
    elif command == "registered":
        _handle_registered(db, chat_id)


def _parse_command(text: str) -> Tuple[Optional[str], List[str]]:
    # Returns command and args if valid, otherwise None
    tokens = [token for token in text.strip().split() if token != ""]
    if len(tokens) == 0:
        return None, []

    command = tokens[0].strip("/")
    if "@" in command:
        command = command.split("@")[0]
    if command in VALID_COMMANDS:
        return command, tokens[1:]
    return None, []


def _handle_sub(db: Session, chat_id: int, args: List[str]):
    if len(args) == 0:
        send_message(chat_id, "Please provide a keyword to subscribe to")
        return

    keyword = args[0]
    alert = crud.add_contract_alert(db, keyword, chat_id)
    if alert:
        send_message(chat_id, f"Added alert for `{keyword}`")
    else:
        send_message(chat_id, f"Alert already exists for `{keyword}`")


def _handle_unsub(db: Session, chat_id: int, args: List[str]):
    if len(args) == 0:
        send_message(chat_id, "Please provide a keyword to unsubscribe to")
        return

    keyword = args[0]
    removed = crud.remove_contract_alert(db, keyword, chat_id)
    if removed:
        send_message(chat_id, f"Removed alert for `{keyword}`")
    else:
        send_message(chat_id, f"No alert exists for `{keyword}`")


def _handle_registered(db: Session, chat_id: int):
    alerts = crud.get_registered_contract_alerts(db, chat_id)
    keywords = [alert.keyword for alert in alerts]
    if len(keywords) > 0:
        keyword_str = ", ".join(keywords)
        send_message(chat_id, f"Current alerts: `[{keyword_str}]`")
    else:
        send_message(chat_id, f"No alerts registered in this chat")
