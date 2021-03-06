import datetime
from typing import Dict, Optional

from pydantic import BaseModel

from app.enums import NetworkID


class VerifiedContractNoData(BaseModel):
    address: str
    name: str
    compiler: str
    version: str
    verified_date: datetime.date
    network_id: NetworkID
    license: Optional[str]

    class Config:
        orm_mode = True


class VerifiedContract(VerifiedContractNoData):
    abi: Optional[str]
    source_code: Optional[str]


class ContractCode(BaseModel):
    name: str
    code: Dict[str, str]
    compiler_version: str
