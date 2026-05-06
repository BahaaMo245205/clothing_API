from pydantic import EmailStr, BaseModel, Field
from typing import Optional, List

# موديل المستخدم
class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str

# موديل المنتج (عشان تستخدمه في الـ POST والـ GET)
class ProductBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    image_url: Optional[str] = None
    stock_quantity: int = 0

# موديل الطلبية
class OrderCreate(BaseModel):
    customer_name: str
    total_price: float
    status: str = "pending"
    # هنا اللعبة: قائمة بالمنتجات اللي جوه الطلبية
    items: List[dict] # مثال: [{"product_id": 1, "quantity": 2}]