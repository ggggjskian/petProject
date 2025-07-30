import datetime
from pydantic import BaseModel, UUID4, field_validator
from typing import Any


class reqAddContract(BaseModel):
    contract_version: str  # По хорошему должна иметь мажор, минор и патч версию и отлавливаться с помощью регулярок формат, пока позже
    contract_obj: dict[str, Any]
    date_from: datetime.datetime
    date_to: datetime.datetime | None

    @field_validator("date_to", mode="after")
    @classmethod
    def checkConsistData(cls, date_to, values):
        date_from = values.data.get("date_from")
        if date_to < date_from:
            raise ValueError("data_from должен быть раньше чем date_to")
        return date_to


class resAddContract(BaseModel):
    status: bool
    id: UUID4 | None


class ContractDB(reqAddContract):
    uuid_obj: UUID4
    hash_contract: str


class responseContract(reqAddContract):
    uuid_obj: UUID4


class reqUpdateContract(BaseModel):
    uuid_obj: UUID4
    contract_version: str
    contract_obj: dict[str, Any]


class resUpdateContract(BaseModel):
    status: bool
    id: int
