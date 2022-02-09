from sqlalchemy import JSON, Column, Date, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Contract(Base):
    __tablename__ = "contracts"

    address = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    compiler = Column(String, nullable=False)
    version = Column(String, nullable=False)
    verified_date = Column(Date, nullable=False)
    abi = Column(JSON, nullable=False)
    license = Column(String)
