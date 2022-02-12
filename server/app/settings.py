import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    telegram_webhook_host = os.environ.get("TELEGRAM_WEBHOOK_HOST")
    telegram_bot_token: str = os.environ.get("TELEGRAM_BOT_TOKEN")
    ftmscan_api_key: str = os.environ.get("FTMSCAN_API_KEY")
    scrape_sleep_sec: int = os.environ.get("SCRAPE_SLEEP_SEC")

    postgres_db: str = os.environ.get("POSTGRES_DB")
    postgres_user: str = os.environ.get("POSTGRES_USER")
    postgres_pw: str = os.environ.get("POSTGRES_PASSWORD")
    postgres_port: int = os.environ.get("POSTGRES_PORT")


settings = Settings()
