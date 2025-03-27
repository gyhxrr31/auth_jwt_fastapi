from authx import AuthX, AuthXConfig
from db_controller.db_controller import Session, r
from fastapi import APIRouter, HTTPException, Form, Response, Request
from sqlmodel import select
from db_schemas.db_schemas import UsersBase, Users
from api.routes.register import get_user_id
from schemas.schemas import RefreshToken
from utils.crypt_pwd import verify_password
from dotenv import load_dotenv

import uuid
import os

auth = APIRouter(prefix="/user/auth", tags=["auth_api"])

load_dotenv()
os.getenv("JWT_SECRET_KEY")


#Настройка jwt токена
config = AuthXConfig()
JWT_HEADER_TYPE = "Bearer" # Тип хедера
JWT_ACCESS_TOKEN_EXPIRES = 60 * 15 #15 минут токен хранится
config.JWT_ALGORITHM = "HS256"
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_TOKEN_LOCATION = ["headers", "cookies", "json"] #Храним токены тут
security = AuthX(config=config)


#Отдельная функция по запросу пароля
async def get_pwd(password: str, username: str):
    async with Session() as session:
        sql_query = select(Users.password).where(Users.username == username and Users.password == password)
        result = session.exec(sql_query)
        return result.one()


#Авторизация по логину и паролю
@auth.post("/login", description="Login for user")
async def login(response: Response, user: UsersBase = Form(...)):
    myuuid = uuid.uuid4()
    username = user.username
    plain_password = r.set(f"user_pwd-{await get_user_id(username)}", user.password)
    async with Session() as session:
        sql_username = select(Users.username).where(Users.username == username)
        result_username = session.exec(sql_username)
        result = result_username.first()
        hashed_password = await get_pwd(r.get(f"reg_password-{await get_user_id(username)}"), r.get(f"reg_username-{await get_user_id(username)}"))
        r.set(f"hashed_password-{await get_user_id(username)}", hashed_password)
        if result == r.get(f"reg_username-{await get_user_id(username)}") and await verify_password(r.get(f"user_pwd-{await get_user_id(username)}"), r.get(f"hashed_password-{await get_user_id(username)}")):#Если юзернейм и хэш пароля совпадают то генерим токен
            token = security.create_access_token(uid=str(myuuid))
            access_token = security.create_access_token(user.username)
            refresh_token = security.create_refresh_token(user.username)
            response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
            return {
                "access_token": access_token,
                "refresh_token": refresh_token
                }
        else:
             raise HTTPException(status_code=401, detail="Username or password is incorrect")


@auth.post("/refresh", description="Refresh token")
async def refresh(request: Request, refresh_data: RefreshToken = None):
    try:
        try:
            refresh_payload = await security.refresh_token_required(request)
        except Exception as header_error:
            if not refresh_data or not refresh_data.refresh_token:
                raise header_error
            token = refresh_data.refresh_token
            refresh_payload = security.verify_token(#Разраба доков ебал в рот за документацию дерьма!
                token,
                verify_type=True,
                type="refresh" # Тот самый аргумент, которого по факту нет, но почему-то он есть! Ебаные классы
            )
        access_token = security.create_access_token(refresh_payload.sub)
        return {"access_token": access_token}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))