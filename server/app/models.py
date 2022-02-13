from sqlalchemy import Column, Computed, Date, Enum, Index, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, TEXT, TIMESTAMP, TSVECTOR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator

from app.enums import NetworkID

Base = declarative_base()


class TSVector(TypeDecorator):
    impl = TSVECTOR
    cache_ok = True


class Contract(Base):
    __tablename__ = "contracts"

    address = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    compiler = Column(String, nullable=False)
    version = Column(String, nullable=False)
    verified_date = Column(Date, nullable=False)
    abi = Column(TEXT, nullable=False)
    source_code = Column(TEXT, nullable=False)
    network_id = Column(Enum(NetworkID), nullable=False)
    timestamp = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    license = Column(String)

    __ts_vector__ = Column(
        TSVector(),
        Computed("to_tsvector('simple', abi || source_code)", persisted=True),
    )

    __table_args__ = (
        Index("ix_contracts___ts_vector__", __ts_vector__, postgresql_using="gin"),
    )


class ContractAlert(Base):
    __tablename__ = "contract_alerts"

    alert_id = Column(Integer, primary_key=True)
    keyword = Column(String, nullable=False, index=True, unique=True)
    chat_ids = Column(ARRAY(Integer), nullable=False)

    __table_args__ = (
        Index("ix_contract_alerts__chat_ids", chat_ids, postgresql_using="gin"),
    )
