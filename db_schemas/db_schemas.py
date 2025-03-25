from sqlmodel import SQLModel, Field, String

class UsersBase(SQLModel):
    username: str = Field(nullable=False, index=True, unique=True)
    password: str = Field(sa_column=(String))



class Users(UsersBase, table=True):
    __tablename__ = 'users'
    id: int | None = Field(default=None, primary_key=True, index=True)
    role: str | None = Field(default='client')

