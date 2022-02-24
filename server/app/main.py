import asyncio
import logging
import os
from pathlib import Path
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import crud
from app.bot import handle_commands, set_telegram_webhook_url
from app.database import get_db
from app.diff import get_base_contract
from app.schemas import ContractCode, VerifiedContract, VerifiedContractNoData
from app.settings import settings
from app.utils import scrape_verified_contracts
from app.web import MAX_FETCH_LIMIT

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Set CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/status", status_code=200)
async def get_status():
    return


@app.get("/api/contract/{address}", status_code=200, response_model=VerifiedContract)
async def get_contract(address: str, db: Session = Depends(get_db)):
    contract = crud.get_contract(db, address=address)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract address not found")
    return contract


@app.get(
    "/api/contracts/", status_code=200, response_model=List[VerifiedContract],
)
async def get_contracts(
    skip: int = 0,
    limit: int = 100,
    most_recent: bool = True,
    include_contract_data: bool = False,
    db: Session = Depends(get_db),
):
    contracts = crud.get_contracts(
        db, skip=skip, limit=min(limit, MAX_FETCH_LIMIT), most_recent=most_recent,
    )
    if include_contract_data:
        return [VerifiedContract.from_orm(c) for c in contracts]
    return [VerifiedContractNoData.from_orm(c) for c in contracts]


@app.get(
    "/api/contracts/search", status_code=200, response_model=List[VerifiedContract]
)
async def get_contracts_search(
    query: str,
    skip: int = 0,
    limit: int = 100,
    most_recent: bool = True,
    include_contract_data: bool = False,
    db: Session = Depends(get_db),
):
    contracts = crud.search_contracts(
        db,
        query,
        skip=skip,
        limit=min(limit, MAX_FETCH_LIMIT),
        most_recent=most_recent,
    )
    if include_contract_data:
        return [VerifiedContract.from_orm(c) for c in contracts]
    return [VerifiedContractNoData.from_orm(c) for c in contracts]


@app.get(
    "/api/base_contract_code/{name}", status_code=200, response_model=ContractCode,
)
async def get_base_contract_code(name: str):
    filepath = f"app/base_contracts/{name}.sol"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Base contract not found")

    base_contract = Path(filepath).read_text()
    contract_code = ContractCode(name=name, base_contract=base_contract)
    return contract_code


@app.get(
    "/api/contract_code/{address}", status_code=200, response_model=ContractCode,
)
async def get_contract_code(
    address: str, db: Session = Depends(get_db),
):
    contract = crud.get_contract(db, address=address)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract address not found")

    base_contract = get_base_contract(contract)
    if not base_contract:
        raise HTTPException(status_code=404, detail="Could not parse base contract")

    contract_code = ContractCode(name=contract.name, base_contract=base_contract)
    return contract_code


@app.get("/api/.*", status_code=404, include_in_schema=False)
async def invalid_api():
    return None


@app.post(f"/webhook/{settings.telegram_bot_token}", include_in_schema=False)
async def post_telegram_update(request: Request):
    body = await request.json()
    message = body.get("message", None)
    if message:
        entities = message.get("entities", [])
        is_command = len(entities) > 0 and entities[0].get("type") == "bot_command"
        if not is_command:
            return
        chat_id = int(message["chat"]["id"])
        text = message["text"]
        try:
            handle_commands(chat_id, text)
        except Exception as e:
            logging.error(e)
    return


@app.on_event("startup")
async def startup_event():
    await set_telegram_webhook_url()
    asyncio.create_task(scrape_verified_contracts())
