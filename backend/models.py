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
    customer_name: str
    total_price: float
    status: str = "pending"
    items: List[dict]  # مثال: [{"product_id": 1, "quantity": 2}]
