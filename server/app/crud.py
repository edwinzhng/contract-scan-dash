import logging
from sqlalchemy.orm import Session

from app import models, schemas

MAX_LIMIT = 500


def get_contract(db: Session, address: str):
    return (
        db.query(models.Contract)
        .filter(models.Contract.address == address.lower())
        .first()
    )


def create_contract(db: Session, contract: schemas.VerifiedContract):
    db_contract = models.Contract(
        address=contract.address.lower(),
        name=contract.name,
        compiler=contract.compiler,
        version=contract.compiler,
        verified_date=contract.verified_date,
        abi=contract.abi,
        network_id=contract.network_id,
        license=contract.license,
    )
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract


def get_contracts(db: Session, skip: int = 0, limit: int = 100):
    limit = min(limit, MAX_LIMIT)
    return db.query(models.Contract).offset(skip).limit(limit).all()


def search_contracts(db: Session, query: str, skip: int = 0, limit: int = 100):
    limit = min(limit, MAX_LIMIT)
    db.query(models.Contract).filter(models.Contract.__ts_vector__.match(query)).all()
    return (
        db.query(models.Contract)
        .filter(models.Contract.__ts_vector__.match(query))
        .offset(skip)
        .limit(limit)
        .all()
    )
