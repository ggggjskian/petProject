import uuid
import psycopg2
import datetime
from typing import Any


from config.dbSettings import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSON


engine = create_async_engine(settings.linkForConnection)
session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    pass


class ContractsORM(Model):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_version: Mapped[str]
    uuid_obj: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True)
    contract_object: Mapped[dict[str, Any]] = mapped_column(JSON)
    hash_contract: Mapped[str]
    date_from: Mapped[datetime.datetime | None]
    date_to: Mapped[datetime.datetime | None]


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
