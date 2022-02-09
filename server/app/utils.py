import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup

from app.crud import create_contract, get_contract
from app.database import get_db
from app.enums import NetworkID
from app.schemas import VerifiedContract
from app.settings import settings

FTMSCAN_CONTRACT_API_URL = "https://api.ftmscan.com/api?module=contract&action=getabi&address={address}&apikey={api_key}"
VERIFIED_CONTRACTS_URL = "https://ftmscan.com/contractsVerified/{page}"
VERIFIED_CONTRACTS_MAX_PAGE = 20


async def scrape_verified_contracts():
    """Scrape new verified contracts on FTMScan"""
    while True:
        contracts_added = 0
        contracts_skipped = 0
        try:
            db = next(get_db())
            for page in range(0, VERIFIED_CONTRACTS_MAX_PAGE + 1):
                contracts = await _scrape_page(page)
                for contract in contracts:
                    if get_contract(db, contract.address) is None:
                        abi = await _fetch_abi(contract.address)
                        contract.abi = abi
                        create_contract(db, contract)
                        contracts_added += 1
                    else:
                        contracts_skipped += 1
        except Exception as e:
            logging.error(e)

        logging.info(f"Added {contracts_added}, skipped {contracts_skipped} contracts")
        await asyncio.sleep(settings.scrape_sleep_sec)


async def _fetch_abi(address: str) -> Dict[Any, Any]:
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(
        None,
        requests.get,
        FTMSCAN_CONTRACT_API_URL.format(
            address=address,
            api_key=settings.ftmscan_api_key,
        ),
    )
    abi = res.json()["result"]
    return abi


async def _scrape_page(page: int, network_id: NetworkID = NetworkID.fantom):
    loop = asyncio.get_event_loop()
    page = await loop.run_in_executor(
        None, requests.get, VERIFIED_CONTRACTS_URL.format(page=page)
    )

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
