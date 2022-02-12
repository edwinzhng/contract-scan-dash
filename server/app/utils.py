import asyncio
import json
import logging
from datetime import datetime
from typing import List, Literal

import requests
from bs4 import BeautifulSoup

from app.crud import create_contract, get_contract
from app.database import get_db
from app.enums import NetworkID
from app.schemas import VerifiedContract
from app.settings import settings

FTMSCAN_CONTRACT_API_URL = "https://api.ftmscan.com/api?module=contract&action={action}&address={address}&apikey={api_key}"
VERIFIED_CONTRACTS_URL = "https://ftmscan.com/contractsVerified/{page}"
VERIFIED_CONTRACTS_MAX_PAGE = 20

TELEGRAM_SET_WEBHOOK_URL = "https://api.telegram.org/bot{token}/setWebhook"


async def get_async(url):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, requests.get, url)


async def post_async(url, data):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, requests.post, url, data)


async def scrape_verified_contracts():
    """Scrape new verified contracts on FTMScan"""
    while True:
        contracts_added = 0
        contracts_skipped = 0
        try:
            db = next(get_db())
            # Iterate backwards so we store the most recent contracts with the latest timestamp
            for page in range(VERIFIED_CONTRACTS_MAX_PAGE, 0, -1):
                contracts = await _scrape_page(page)
                for contract in contracts:
                    if get_contract(db, contract.address) is None:
                        abi = await _fetch_contract_data(contract.address, "getabi")
                        source_code = await _fetch_contract_data(
                            contract.address, "getsourcecode"
                        )

                        contract.abi = abi
                        contract.source_code = source_code
                        create_contract(db, contract)
                        contracts_added += 1
                    else:
                        contracts_skipped += 1
        except Exception as e:
            logging.error(e)

        logging.info(f"Added {contracts_added}, skipped {contracts_skipped} contracts")
        await asyncio.sleep(settings.scrape_sleep_sec)


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


async def _fetch_contract_data(
    address: str, action: Literal["getabi", "getsourcecode"]
) -> str:
    # Retry in case of rate limit
    while True:
        ftmscan_url = FTMSCAN_CONTRACT_API_URL.format(
            action=action,
            address=address,
            api_key=settings.ftmscan_api_key,
        )
        res = await get_async(ftmscan_url)
        data = res.json()["result"]
        data_str = json.dumps(data)
        if "rate limit reached" not in data_str.strip().lower():
            return data_str
        await asyncio.sleep(1)


async def _scrape_page(page: int, network_id: NetworkID = NetworkID.fantom):
    page = await get_async(VERIFIED_CONTRACTS_URL.format(page=page))
    soup = BeautifulSoup(page.text, features="html.parser")

    # Find index of data in table based on header
    header = soup.find("thead").find("tr")
    header_cells = header.find_all("th")
    header_names = [cell.text.strip() for cell in header_cells]
    names_to_save = [
        "Address",
        "Contract Name",
        "Compiler",
        "Version",
        "Verified",
        "License",
    ]
    data_idx = [header_names.index(name) for name in names_to_save]

    # Parse results from table rows
    results: List[VerifiedContract] = []
    body = soup.find("tbody")
    rows = body.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        row_values = [cell.text.strip() for cell in cells]
        addr, name, compiler, version, dt, license = [row_values[i] for i in data_idx]
        verified_dt = datetime.strptime(dt, "%m/%d/%Y")
        results.append(
            VerifiedContract(
                address=addr,
                name=name,
                compiler=compiler,
                version=version,
                verified_date=verified_dt,
                network_id=network_id,
                license=license if license != "-" else None,
            )
        )

    return results
