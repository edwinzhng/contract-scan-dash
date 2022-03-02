import asyncio
import json
import logging
from datetime import datetime
from typing import List, Literal

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

import app.crud as crud
from app.bot import send_message
from app.database import get_db
from app.diff import get_closest_base_contract
from app.enums import NetworkID
from app.models import Contract, ContractAlert
from app.schemas import VerifiedContract
from app.settings import settings
from app.web import get_async

FTMSCAN_CONTRACT_API_URL = "https://api.ftmscan.com/api?module=contract&action={action}&address={address}&apikey={api_key}"
VERIFIED_CONTRACTS_URL = "https://ftmscan.com/contractsVerified/{page}"
VERIFIED_CONTRACTS_MAX_PAGE = 20

DIFF_BASE_URL = "https://rocketpooldata.com/diff"


async def scrape_verified_contracts():
    """Scrape new verified contracts on FTMScan"""
    while True:
        contracts_added = 0
        contracts_skipped = 0
        new_addresses = []
        try:
            db = next(get_db())
            # Iterate backwards so we store the most recent contracts with the latest timestamp
            for page in range(VERIFIED_CONTRACTS_MAX_PAGE, 0, -1):
                contracts = await _scrape_page(page)
                for contract in contracts:
                    if crud.get_contract(db, contract.address) is None:
                        abi = await _fetch_contract_data(contract.address, "getabi")
                        source_code = await _fetch_contract_data(
                            contract.address, "getsourcecode"
                        )
                        contract.abi = abi
                        contract.source_code = source_code

                        db_contract = crud.create_contract(db, contract)
                        contracts_added += 1
                        new_addresses.append(db_contract.address)
                    else:
                        contracts_skipped += 1
        except Exception as e:
            logging.error(e)

        logging.info(f"Added {contracts_added}, skipped {contracts_skipped} contracts")
        if contracts_added >= 0:
            await send_telegram_alerts(new_addresses)
        await asyncio.sleep(settings.scrape_sleep_sec)


async def send_telegram_alerts(new_addresses: List[str]):
    db: Session = next(get_db())
    chat_id_to_alerts = {}
    new_contracts = crud.get_contracts_by_addresses(db, new_addresses)
    for alert in db.query(ContractAlert).filter(ContractAlert.chat_ids != "{}"):
        try:
            keyword = alert.keyword
            matches = new_contracts.filter(Contract.search(keyword)).all()
            if len(matches) == 0:
                continue

            match_base_contracts = get_closest_base_contract(matches)
            diff_links = [
                _format_diff_link(m, base_contract)
                for m, base_contract in zip(matches, match_base_contracts)
            ]
            match_links = [_format_contract_link(m) for m in matches]
            logging.info(f"Matches for '{keyword}': {match_links}")
            logging.info(f"Closest base contracts: {match_base_contracts}")

            for chat_id in alert.chat_ids:
                existing_alerts = chat_id_to_alerts.get(chat_id, [])
                existing_alerts.append((keyword, match_links, diff_links))
                chat_id_to_alerts[chat_id] = existing_alerts
        except Exception as e:
            logging.error(e)

    chat_ids = list(chat_id_to_alerts.keys())
    if len(chat_ids) == 0:
        return

    logging.info(f"Sending alerts to {chat_ids}")
    for chat_id in chat_ids:
        try:
            alerts = chat_id_to_alerts[chat_id]
            message = "*New contracts matching alerts*\n"
            for keyword, match_links, diff_links in alerts:
                message += f"`{keyword}`\n"
                for match, diff in zip(match_links, diff_links):
                    message += f"  * {match} -- {diff}\n"
            send_message(chat_id, message)
        except Exception as e:
            logging.error(e)


async def _fetch_contract_data(
    address: str, action: Literal["getabi", "getsourcecode"]
) -> str:
    # Retry in case of rate limit
    while True:
        ftmscan_url = FTMSCAN_CONTRACT_API_URL.format(
            action=action, address=address, api_key=settings.ftmscan_api_key,
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
                address=str(addr).lower(),
                name=name,
                compiler=compiler,
                version=version,
                verified_date=verified_dt,
                network_id=network_id,
                license=license if license != "-" else None,
            )
        )

    return results


def _format_contract_link(contract: Contract):
    url = f"https://ftmscan.com/address/{contract.address}"
    short_addr = contract.address[0:6] + "..." + contract.address[-4:]
    return f"[{contract.name} ({short_addr})]({url})"


def _format_diff_link(contract: Contract, base_contract_name: str):
    url = f"{DIFF_BASE_URL}?diff_name={base_contract_name}&addr={contract.address}"
    return f"[Diff]({url}) with {base_contract_name}"
