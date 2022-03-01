import asyncio
import logging
import os
from pathlib import Path
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app import crud
from app.bot import handle_commands, set_telegram_webhook_url
from app.database import get_db
from app.diff import contracts_to_code, parse_contract_code
from app.schemas import ContractCode, VerifiedContract, VerifiedContractNoData
from app.settings import settings
from app.utils import scrape_verified_contracts
from app.web import MAX_FETCH_LIMIT

CLIENT_BUILD_PATH = "app/public"

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

app.mount(
    "/static/", StaticFiles(directory=f"{CLIENT_BUILD_PATH}/static"), name="static"
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
    filedir = f"app/base_contracts/{name}/"
    if not os.path.exists(filedir):
        raise HTTPException(status_code=404, detail="Base contract not found")
    
    files = os.listdir(filedir)
    file_strs = []
    for f in files:
        f_path = os.path.join(filedir, f)
        if os.path.isfile(f_path):
            file_strs.append(Path(f_path).read_text())
    
    code = contracts_to_code("\n".join(file_strs))
    contract_code = ContractCode(name=name, code=code)
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

    code = parse_contract_code(contract)
    if not code:
        raise HTTPException(status_code=404, detail="Could not parse base contract")

    contract_code = ContractCode(name=contract.name, code=code, solidity_version=contract.version)
    return contract_code


@app.get("/api/{catchall:path}", status_code=404, include_in_schema=False)
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


@app.get("/", include_in_schema=False)
def read_index():
    return FileResponse(f"{CLIENT_BUILD_PATH}/index.html")


@app.get("/{catchall:path}", response_class=FileResponse)
def read_index(request: Request):
    path = request.path_params["catchall"]
    file = f"{CLIENT_BUILD_PATH}/{path}"
    if os.path.exists(file):
        return FileResponse(file)

    index = f"{CLIENT_BUILD_PATH}/index.html"
    return FileResponse(index)


@app.on_event("startup")
async def startup_event():
    await set_telegram_webhook_url()
    asyncio.create_task(scrape_verified_contracts())
