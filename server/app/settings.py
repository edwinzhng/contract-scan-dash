import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    postgres_db: str = os.environ.get("POSTGRES_DB")
    postgres_user: str = os.environ.get("POSTGRES_USER")
    postgres_pw: str = os.environ.get("POSTGRES_PASSWORD")
    postgres_port: int = os.environ.get("POSTGRES_PORT")
    ftmscan_api_key: str = os.environ.get("FTMSCAN_API_KEY")
    scrape_sleep_sec: int = os.environ.get("SCRAPE_SLEEP_SEC")


settings = Settings()
