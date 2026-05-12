from pydantic import EmailStr, BaseModel, Field
from typing import Optional, List


class InfoUser(BaseModel):
    IdUser : Optional[int] = None
    image: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    Address: Optional[str] = None


class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    Info: InfoUser


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# موديل الطلبية
class OrderCreate(BaseModel):
    product_id : int
    customer_id: int
    count : int
