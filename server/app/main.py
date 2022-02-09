import asyncio
import logging
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import VerifiedContract, VerifiedContractNoData
from app.utils import scrape_verified_contracts

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
    "/api/contracts/",
    status_code=200,
    response_model=List[VerifiedContract],
)
async def get_contracts(
    skip: int = 0,
    limit: int = 100,
    most_recent: bool = True,
    include_contract_data: bool = False,
    db: Session = Depends(get_db),
):
    contracts = crud.get_contracts(
        db,
        skip=skip,
        limit=limit,
        most_recent=most_recent,
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
        limit=limit,
        most_recent=most_recent,
    )
    if include_contract_data:
        return [VerifiedContract.from_orm(c) for c in contracts]
    return [VerifiedContractNoData.from_orm(c) for c in contracts]


@app.get("/api/.*", status_code=404, include_in_schema=False)
def invalid_api():
    return None


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(scrape_verified_contracts())
