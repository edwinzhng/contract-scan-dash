import datetime
from typing import Optional

from pydantic import BaseModel

from app.enums import NetworkID


class VerifiedContract(BaseModel):
    address: str
    name: str
    compiler: str
    version: str
    verified_date: datetime.date
    network_id: NetworkID
    license: Optional[str]
    abi: Optional[str]

    class Config:
        orm_mode = True
