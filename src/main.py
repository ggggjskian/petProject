from fastapi import FastAPI, Path
from fastapi.exceptions import HTTPException
from modules.DB.database import (
    create_tables,
    delete_tables,
    addContract,
    getActualContract,
    getHistoryContract,
    updateVersionContract,
)
from contextlib import asynccontextmanager
from models.shemas import (
    resAddContract,
    reqAddContract,
    responseContract,
    reqUpdateContract,
    resUpdateContract,
)
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


@app.post("/addContract")
async def add_contract(contract_entity: reqAddContract) -> resAddContract:
    uuid, id = await addContract(contract_entity)
    if id is None:
        raise HTTPException(status_code=400, detail="Ошибка добавление контракта")

    print(uuid)
    print(id)
    res = resAddContract(status=True, id=uuid)
    return res


@app.post("/updateContract")
async def update_contract(contract_entity: reqUpdateContract) -> resUpdateContract:
    upDating = reqUpdateContract(**contract_entity.model_dump())
    getActContract = await getActualContract(upDating.uuid_obj)

    if getActContract is None:
        raise HTTPException(
            status_code=404,
            detail="Контракт для которого вы пытаетесь обновить версию, не существует",
        )

    if getActContract.contract_version == upDating.contract_version:
        raise HTTPException(
            status_code=400, detail="Версия контракта соотвествует старой"
        )

    check = await updateVersionContract(getActContract, upDating)

    if check == -1:
        raise HTTPException(
            status_code=400, detail="Отсутствуют обновления в теле вашего контракта"
        )

    answer = resUpdateContract(status=True, id=check)

    return answer


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


@app.get("/getContractHistory")
async def get_history_contract(item_id: UUID) -> list[responseContract]:
    contracts = await getHistoryContract(item_id)
    if contracts is None:
        raise HTTPException(
            status_code=404, detail="История данного контракта не найдена"
        )

    responces = []

    for con in contracts:
        responseData = responseContract(
            uuid_obj=con.uuid_obj,
            contract_version=con.contract_version,
            contract_obj=con.contract_obj,
            hash_contract=con.hash_contract,
            date_from=con.date_from,
            date_to=con.date_to,
        )
        responces.append(responseData)

    return responces


@app.get("/")
async def read_info():
    return {"Hello": "Async World"}
