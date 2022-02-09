import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class VerifiedContract(BaseModel):
    address: str
    name: str
    compiler: str
    version: str
    verified_date: datetime.date
    license: Optional[str]
    abi: Optional[str]

    class Config:
        orm_mode = True
