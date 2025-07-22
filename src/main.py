from fastapi import FastAPI
from modules.DB.database import create_tables, delete_tables
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await delete_tables()
    print("База очищена")
    await create_tables()
    print("База готова к работе")
    yield
    print("Выключение")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_info():
    return {"Hello": " World"}


@app.post("/addContract")
def add_contract():
    pass


@app.get("/getContract")
def add_contract():
    pass