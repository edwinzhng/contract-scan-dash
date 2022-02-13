from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.models import Contract, ContractAlert
from app.schemas import VerifiedContract

MAX_LIMIT = 500


def get_contract(db: Session, address: str):
    return db.query(Contract).filter(Contract.address == address.lower()).first()


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
    limit = min(limit, MAX_LIMIT)
    order_clause = (
        Contract.timestamp.desc() if most_recent else Contract.timestamp.asc()
    )
    return db.query(Contract).order_by(order_clause).offset(skip).limit(limit).all()


def search_contracts(
    db: Session, query: str, skip: int = 0, limit: int = 100, most_recent: bool = True
):
    limit = min(limit, MAX_LIMIT)
    order_clause = (
        Contract.timestamp.desc() if most_recent else Contract.timestamp.asc()
    )
    return (
        db.query(Contract)
        .filter(Contract.__ts_vector__.op("@@")(func.plainto_tsquery("simple", query)))
        .order_by(order_clause)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_registered_contract_alerts(db: Session, chat_id: int):
    return (
        db.query(ContractAlert).filter(ContractAlert.chat_ids.contains([chat_id])).all()
    )


def add_contract_alert(db: Session, keyword: str, chat_id: int):
    alert = db.query(ContractAlert).filter(ContractAlert.keyword == keyword).first()
    if alert:
        if chat_id not in alert.chat_ids:
            alert.chat_ids.append(chat_id)
            flag_modified(alert, "chat_ids")
        else:
            return None  # Alert already exists for chat_id
    else:
        alert = ContractAlert(keyword=keyword, chat_ids=[chat_id])
        db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def remove_contract_alert(db: Session, keyword: str, chat_id: int) -> bool:
    alert = (
        db.query(ContractAlert)
        .filter(ContractAlert.keyword == keyword)
        .filter(ContractAlert.chat_ids.contains([chat_id]))
        .first()
    )
    if alert:
        alert.chat_ids.remove(chat_id)
        flag_modified(alert, "chat_ids")
        db.commit()
        db.refresh(alert)
        return True
    return False
