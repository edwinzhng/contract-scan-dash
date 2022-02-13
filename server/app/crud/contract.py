from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Contract
from app.schemas import VerifiedContract
from app.web import MAX_FETCH_LIMIT


def get_contract(db: Session, address: str):
    return db.query(Contract).filter(Contract.address == address.lower()).first()


def get_contracts_by_addresses(db: Session, addresses: List[str]):
    addresses = [addr.lower() for addr in addresses]
    return db.query(Contract).filter(Contract.address.in_(addresses))


def create_contract(db: Session, contract: VerifiedContract):
    db_contract = Contract(
        address=contract.address.lower(),
        name=contract.name,
        compiler=contract.compiler,
        version=contract.compiler,
        verified_date=contract.verified_date,
        abi=contract.abi,
        source_code=contract.source_code,
        network_id=contract.network_id,
        license=contract.license,
    )
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract


def get_contracts(
    db: Session, skip: int = 0, limit: int = 100, most_recent: bool = True
):
    limit = min(limit, MAX_FETCH_LIMIT)
    order_clause = (
        Contract.timestamp.desc() if most_recent else Contract.timestamp.asc()
    )
    return db.query(Contract).order_by(order_clause).offset(skip).limit(limit)


def search_contracts(
    db: Session, query: str, skip: int = 0, limit: int = 100, most_recent: bool = True
):
    limit = min(limit, MAX_FETCH_LIMIT)
    order_clause = (
        Contract.timestamp.desc() if most_recent else Contract.timestamp.asc()
    )
    return (
        db.query(Contract)
        .filter(Contract.search(query))
        .order_by(order_clause)
        .offset(skip)
        .limit(limit)
    )
