import datetime
from typing import Optional

from pydantic import BaseModel
import telegram

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


class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[telegram.Message]
    my_chat_member: Optional[telegram.ChatMemberUpdated]

    class Config:
        arbitrary_types_allowed = True
