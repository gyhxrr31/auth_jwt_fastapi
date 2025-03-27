from db_controller.db_controller import Session, r
from fastapi import APIRouter, HTTPException
from db_schemas.db_schemas import UsersBase, Users
from sqlmodel import select
from utils.crypt_pwd import hasher_pwd


user_register = APIRouter(prefix="/user", tags=["register"])

#Будем юзать id юзеров для идентификации значений в redis
async def get_user_id(username: str):
    async with Session() as session:
        sql_query = select(Users.id).where(Users.username == username and Users.username == username)
        result = session.exec(sql_query)
        return result.one()


#Регистрация с хэшированием пароля
@user_register.post("/register", description="Register new user with client role")
async def register_user(user: UsersBase):
    password = await hasher_pwd(user.password)
    username = user.username
    async with Session() as session:
        user = Users(username=username, password=password)
        session.add(user)
        session.commit()
        session.refresh(user)
        if user:
            unique_username_id = await get_user_id(username)
            r.set(f"reg_password-{unique_username_id}", password)
            r.set(f"reg_username-{unique_username_id}", username)
            return {"Message": "User registered successfully"}
        else:
            raise HTTPException(error=401, detail="Username already registered, try again")