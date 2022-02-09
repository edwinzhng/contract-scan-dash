from sqlalchemy import Column, Computed, Date, Enum, Index, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base

from app.enums import NetworkID

Base = declarative_base()


class Contract(Base):
    __tablename__ = "contracts"

    address = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    compiler = Column(String, nullable=False)
    version = Column(String, nullable=False)
    verified_date = Column(Date, nullable=False)
    abi = Column(JSON, nullable=False)
    network_id = Column(Enum(NetworkID), nullable=False)
    license = Column(String)
