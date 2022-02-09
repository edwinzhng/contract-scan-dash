import asyncio
import logging
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import VerifiedContract
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


@app.get("/v1/status", status_code=200)
async def get_status():
    return


@app.get("/v1/contract/{address}", status_code=200, response_model=VerifiedContract)
async def get_contract(address: str, db: Session = Depends(get_db)):
    contract = crud.get_contract(db, address=address)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract address not found")
    return contract


@app.get("/v1/contracts/", status_code=200, response_model=List[VerifiedContract])
async def get_contracts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contracts = crud.get_contracts(db, skip=skip, limit=limit)
    return contracts


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(scrape_verified_contracts())
