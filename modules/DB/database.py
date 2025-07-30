import uuid
import json
from datetime import datetime, timezone
from typing import Any


from config.dbSettings import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSON, TIMESTAMP
from sqlalchemy import select, update

from modules.DB.helpFunc import toHash
from models.shemas import reqAddContract, ContractDB, reqUpdateContract


engine = create_async_engine(settings.linkForConnection)
session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    pass


class ContractsORM(Model):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_version: Mapped[str]
    uuid_obj: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    contract_obj: Mapped[dict[str, Any]] = mapped_column(JSON)
    hash_contract: Mapped[str]
    date_from: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    date_to: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))


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
async def addContract(
    db_contract: reqAddContract, session: AsyncSession
) -> tuple[UUID, int]:
    obj_str = json.dumps(
        db_contract.contract_obj, sort_keys=True, separators=(",", ":")
    )
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
async def getActualContract(uuid_obj: UUID, session: AsyncSession) -> ContractsORM:
    stmt = select(ContractsORM).where(ContractsORM.uuid_obj == uuid_obj)
    result = await session.execute(stmt)
    if result is None:
        return None

    tempResult = result.scalars().all()[-1]
    local_time = datetime.now(timezone.utc)
    if not (tempResult.date_to is None):
        if tempResult.date_to < local_time:
            return None
    return tempResult


@connection
async def getHistoryContract(
    uuid_obj: UUID, session: AsyncSession
) -> list[ContractsORM]:
    stmt = select(ContractsORM).where(ContractsORM.uuid_obj == uuid_obj)
    result = await session.execute(stmt)
    return result.scalars().all()


@connection
async def updateVersionContract(
    oldVersion: ContractsORM, update: reqUpdateContract, session: AsyncSession
) -> int:
    newStrObj = json.dumps(update.contract_obj, sort_keys=True, separators=(",", ":"))
    newStrObjHash = await toHash(newStrObj)
    if oldVersion.hash_contract == newStrObjHash:
        return -1  # генерация HTTPExeption

    upDatingContract = ContractsORM(
        **update.model_dump(),
        hash_contract=newStrObjHash,
        date_from=oldVersion.date_to,
        date_to=None,
    )

    if oldVersion.date_to is None:
        updateOldDate(oldVersion, upDatingContract.date_from)

    session.add(upDatingContract)
    await session.flush()
    await session.refresh(upDatingContract)

    return upDatingContract.id


@connection
async def updateOldDate(oldVersionContract: ContractsORM, newDateTo: datetime, session):
    stmt = (
        update(ContractsORM)
        .where(ContractsORM=oldVersionContract)
        .values(date_to=newDateTo)
    )
    result = await session.execute(stmt)
    return result
