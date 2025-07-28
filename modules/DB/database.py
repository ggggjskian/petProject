import uuid
import json
import psycopg2
import datetime
from typing import Any


from config.dbSettings import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSON, TIMESTAMP
from sqlalchemy import select

from modules.DB.helpFunc import toHash
from models.shemas import reqAddContract, ContractDB


engine = create_async_engine(settings.linkForConnection)
session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    pass


class ContractsORM(Model):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_version: Mapped[str]
    uuid_obj: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True)
    contract_obj: Mapped[dict[str, Any]] = mapped_column(JSON)
    hash_contract: Mapped[str]
    date_from: Mapped[datetime.datetime | None] = mapped_column(
        TIMESTAMP(timezone=True)
    )
    date_to: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP(timezone=True))


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)


def connection(method):
    async def wrapper(*args, **kwargs):
        async with session() as sn:
            try:
                result = await method(*args, session=sn, **kwargs)
                await sn.commit()
                return result
            except Exception as e:
                await sn.rollback()
                raise e
            finally:
                await sn.close()

    return wrapper


@connection
async def addContract(db_contract: reqAddContract, session) -> tuple[UUID, int]:
    tempObj = db_contract.contract_obj
    obj_str = json.dumps(tempObj, sort_keys=True, separators=(",", ":"))
    hashObj = await toHash(obj_str)
    uuidObj = uuid.uuid4()

    contract_to_DB = ContractDB(
        **db_contract.model_dump(), uuid_obj=uuidObj, hash_contract=hashObj
    )

    contract = ContractsORM(**contract_to_DB.model_dump())
    session.add(contract)
    await session.flush()
    await session.refresh(contract)

    return contract.uuid_obj, contract.id


@connection
async def getActualContract(uuid_obj: UUID, session) -> ContractsORM:
    stmt = select(ContractsORM).where(ContractsORM.uuid_obj == uuid_obj)
    result = await session.execute(stmt)
    return result.scalars().first()
