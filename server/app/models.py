from sqlalchemy import Column, Computed, Date, Enum, Index, String
from sqlalchemy.dialects.postgresql import TEXT, TSVECTOR
from sqlalchemy.ext.declarative import declarative_base
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
    network_id = Column(Enum(NetworkID), nullable=False)
    license = Column(String)

    __ts_vector__ = Column(
        TSVector(),
        Computed("to_tsvector('simple', abi)", persisted=True),
    )

    __table_args__ = (
        Index("ix_contracts___ts_vector__", __ts_vector__, postgresql_using="gin"),
    )
