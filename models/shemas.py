import datetime
import uuid
from pydantic import BaseModel
from typing import Any


class reqAddContract(BaseModel):
    contract_version: str
    contact_obj: dict[str, Any]
    date_from: datetime.datetime
    date_to: datetime.datetime | None


class resAddContract(BaseModel):
    statis: bool
    id: uuid.UUID | None
