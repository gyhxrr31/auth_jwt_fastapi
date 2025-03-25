from passlib.context import CryptContext
import bcrypt

#Чтоб не выебывалось с ошибкой
bcrypt.__about__ = bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Хэшируем пароль
async def hasher_pwd(password: str) :
    return pwd_context.hash(password)

#Проверяем хэш пароля и сам пароль
async def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)