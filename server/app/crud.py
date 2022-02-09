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
        license=contract.license,
    )
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract


def get_contracts(db: Session, skip: int = 0, limit: int = 100):
    limit = min(limit, MAX_LIMIT)
    logging.info(db.query(models.Contract).all()[0])
    return db.query(models.Contract).offset(skip).limit(limit).all()
