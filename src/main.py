from fastapi import FastAPI, Path
from modules.DB.database import create_tables, delete_tables
from contextlib import asynccontextmanager
from models.shemas import resAddContract, reqAddContract
from datetime import datetime
from uuid import UUID


@asynccontextmanager
async def lifespan(app: FastAPI):
    await delete_tables()
    print("База очищена")
    await create_tables()
    print("База готова к работе")
    yield
    print("Выключение")


app = FastAPI(lifespan=lifespan, title="СRU operation with contract's info")


@app.get("/")
async def read_info():
    return {"Hello": " Async World"}


@app.post("/addContract")
async def add_contract(contract_entity: reqAddContract) -> resAddContract:
    pass


@app.post("/updateContract")
async def update_contract():
    pass


@app.get("/getContract/{idContract}")
async def get_contract(
    item_id: UUID = Path(..., description="ID элемента"),
):
    pass
