from fastapi import FastAPI, Path
from fastapi.exceptions import HTTPException
from modules.DB.database import (
    create_tables,
    delete_tables,
    addContract,
    getActualContract,
)
from contextlib import asynccontextmanager
from models.shemas import resAddContract, reqAddContract, responseContract
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
    uuid, id = await addContract(contract_entity)
    print(uuid)
    print(id)
    res = resAddContract(status=True, id=uuid)
    return res


@app.post("/updateContract")
async def update_contract():
    pass


@app.get("/getContract/")
async def get_contract(item_id: UUID) -> responseContract:
    contract = await getActualContract(item_id)

    if contract is None:
        raise HTTPException(status_code=404, detail="Контракт не найден")

    responseData = responseContract(
        uuid_obj=contract.uuid_obj,
        contract_version=contract.contract_version,
        contract_obj=contract.contract_obj,
        hash_contract=contract.hash_contract,
        date_from=contract.date_from,
        date_to=contract.date_to,
    )

    return responseData
