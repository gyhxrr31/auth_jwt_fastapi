from fastapi import APIRouter
from sqlmodel import SQLModel, create_engine
from sqlmodel import Session as DBSession
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from loguru import logger


import redis
import os

load_dotenv()


db_user = os.getenv("POSTGRES_USER")
db_pwd = os.getenv("POSTGRES_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("POSTGRES_DB")
redis_password = os.getenv("REDIS_PASSWORD")

PG_DATABASE_URL = f'postgresql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}'
engine = create_engine(PG_DATABASE_URL, pool_reset_on_return=None, pool_recycle=3600)

r = redis.Redis(host='redis', password=redis_password, port=6379, decode_responses=True)


#Создаем сессию для БД которая будет нормально открываться и закрываться.
@asynccontextmanager
async def Session():
    session = DBSession(engine)
    try:
        logger.info("Starting session")
        yield session
    except Exception as e:
        logger.error(f"Error {e}")
    finally:
       session.close()
       logger.info("Session finished")


#Засовываем сюда то, что необходимо включать при запуске, например сессию редиса
@asynccontextmanager
async def lifespan(app: APIRouter):
    try:
        r.client()
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        logger.error(f"Error {e}")
    finally:
        yield
        r.close()
        engine.dispose()



db_control = APIRouter(prefix="/db_controller", tags=["db_controller"], lifespan=lifespan)