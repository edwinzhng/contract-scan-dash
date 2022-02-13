from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.models import ContractAlert


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
