from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: int
    password_hash: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
