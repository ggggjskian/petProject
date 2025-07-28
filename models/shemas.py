import datetime
from pydantic import BaseModel, UUID4
from typing import Any


class reqAddContract(BaseModel):
    contract_version: str
    contract_obj: dict[str, Any]
    date_from: datetime.datetime
    date_to: datetime.datetime | None


class resAddContract(BaseModel):
    status: bool
    id: UUID4 | None


class ContractDB(reqAddContract):
    uuid_obj: UUID4
    hash_contract: str


class responseContract(reqAddContract):
    uuid_obj: UUID4
