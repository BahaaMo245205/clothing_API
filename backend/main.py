from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from ConnactSQL import Sql
from backend.models import UserRegistration, OrderCreate, InfoUser, UserLogin
from datetime import datetime
import hashlib

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"
PRODUCT_IMAGES_DIR = BASE_DIR.parent / "Clothings_Photo"
DB_PATH = BASE_DIR.parent / "database" / "shop.db"

app = FastAPI(description="""This Project About Clothing Store""", version="1.0.0")
sql = Sql(str(DB_PATH))

if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
if not PRODUCT_IMAGES_DIR.exists():
    PRODUCT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/Clothings_Photo", StaticFiles(directory=str(PRODUCT_IMAGES_DIR)), name="product_images")


@app.get("/", response_class=HTMLResponse)
async def home_page():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return FileResponse(str(FRONTEND_DIR / "login.html"))


@app.get("/signup", response_class=HTMLResponse)
async def signup_page():
    return FileResponse(str(FRONTEND_DIR / "signup.html"))


# ============================(Users)=======================
@app.get("/AllUsers")
async def GetAllUsers():
    query = """
    SELECT 
        u.id, u.username, u.email, u.password,
        i.Image, i.Phone, i.Address
    FROM users u
    LEFT JOIN InfoUser i ON u.id = i.IdUser
    """

    fetched_data = sql.RunCode(query)
    result = []

    for row in fetched_data:
        user_id = row[0]

        # جلب الأوردرات وتحويلها لـ List of Dicts عشان تكون مفهومة في الـ Frontend
        orders_data = sql.RunCode(
            "SELECT id, total_price, Date, status FROM orders WHERE customer_id=?",
            (user_id,),
        )
        user_orders = []
        for o in orders_data:
            user_orders.append(
                {"order_id": o[0], "total": o[1], "date": o[2], "status": o[3]}
            )

        result.append(
            {
                "id": user_id,
                "username": row[1],
                "email": row[2],
                "info": {
                    "image": row[4],
                    "phone": row[5],
                    "Address": row[6],
                },
                "Orders": user_orders,
            }
        )

    return result


@app.post("/Signup")
async def signup(NewUser: UserRegistration):

    if NewUser.confirm_password == NewUser.password:
        user_exists = sql.RunCode(
            "SELECT email FROM users WHERE email=?", (NewUser.email,)
        )
        if user_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="هذا البريد الإلكتروني مسجل بالفعل",
            )
        HashPassword = hashlib.sha256(NewUser.password.encode()).hexdigest()
        NewUser.password = HashPassword
        success = sql.RunCode(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (NewUser.username, NewUser.email, NewUser.password),
        )
        if success:
            return {"status": "success", "message": "تم إنشاء الحساب بنجاح"}
        else:
            return {"Massage": "Please ,You have Error"}

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="كلمات المرور غير متطابقة"
        )


@app.post("/api/signup")
async def api_signup(NewUser: UserRegistration):
    return await signup(NewUser)


@app.post("/Login")
async def login(UserLoginRequest: UserLogin):
    hashed_input = hashlib.sha256(UserLoginRequest.password.encode()).hexdigest()

    result = sql.RunCode(
        "SELECT email, password, username FROM users WHERE email=? AND password=?",
        (
            UserLoginRequest.email,
            hashed_input,
        ),
    )

    if not result:
        raise HTTPException(status_code=401, detail="الايميل غير موجود")

    db_email = result[0][0]
    db_password = result[0][1]

    if hashed_input == db_password:
        return {
            "status": "Success",
            "message": f"Welcome back, {result[0][2]}",
            "user_info": {"email": db_email, "name": result[0][2]},
        }
    else:
        raise HTTPException(status_code=401, detail="كلمة المرور غير صحيحة")


@app.post("/api/login")
async def api_login(UserLoginRequest: UserLogin):
    return await login(UserLoginRequest)


@app.post("/AddInforUser")
async def AddInformationUser(infouser: InfoUser):
    """Add another information data User"""

    query = "INSERT INTO InfoUser (IdUser, Image, Phone, Address) VALUES (?, ?, ?, ?)"
    params = (infouser.IdUser, infouser.image, infouser.phone, infouser.Address)

    success = sql.RunCode(query, params)

    if success:
        return {
            "status": "success",
            "message": f"Added Information User success for ID: {infouser.IdUser}",
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not add information. Check if IdUser exists or data is valid.",
        )


@app.post("/UpdatePassword")
async def update_password(
    email: str, old_password, new_password: str, confirm_password: str
):
    hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
    hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
    codeSql = "SELECT password FROM users WHERE email=? AND password=?"
    result = sql.RunCode(
        codeSql,
        (
            email,
            hashed_old_password,
        ),
    )
    print(result)
    if result:
        if new_password != confirm_password:
            raise HTTPException(status_code=400, detail="كلمات المرور غير متطابقة")

        sql.RunCode(
            "UPDATE users SET password=? WHERE email=?", (hashed_new_password, email)
        )
        return {"message": "Password updated successfully"}

    else:
        raise HTTPException(status_code=401, detail="كلمة المرور القديمة غير صحيحة")


@app.put("/UpdateInforUser")
async def UpdateInformationUser(infouser: InfoUser):

    query = "UPDATE InfoUser SET Image=?, Phone=?, Address=? WHERE IdUser=?"

    params = (infouser.image, infouser.phone, infouser.Address, infouser.IdUser)

    success = sql.RunCode(query, params)

    if success:
        return {
            "status": "success",
            "message": "Updated Information User success",
            "data": {"id": infouser.IdUser},
        }
    else:
        raise HTTPException(
            status_code=400, detail="Update failed. Check if IdUser exists."
        )


# ============================(Users)=======================


# ============================(Products)=======================
@app.get("/api/products", description="""Get All Data about Clothing""")
async def GetAllProducts():
    result = []
    fetched_product = sql.RunCode("SELECT * FROM products")
    num_product = len(fetched_product)
    for i in range(num_product):
        result.append(
            {
                "id": fetched_product[i][0],
                "name": fetched_product[i][1],
                "price": fetched_product[i][2],
                "description": fetched_product[i][3],
                "image_url": fetched_product[i][4],
                "stock_quantity": fetched_product[i][5] if len(fetched_product[i]) > 5 else 0,
            }
        )

    return result

@app.post("/CreateOrder")
async def create_order(order: OrderCreate):
    product_data = sql.RunCode(
        "SELECT price, stock_quantity FROM products WHERE id=?", (order.product_id,)
    )
    if not product_data:
        raise HTTPException(status_code=404, detail="المنتج غير موجود")

    price_product = product_data[0][0]
    current_stock = product_data[0][1]

    if current_stock < order.count:
        raise HTTPException(
            status_code=400, detail=f"عفواً، الكمية المتاحة {current_stock} فقط"
        )

    user_info = sql.RunCode(
        "SELECT username FROM users WHERE id=?", (order.customer_id,)
    )
    address_info = sql.RunCode(
        "SELECT Address FROM InfoUser WHERE IdUser=?", (order.customer_id,)
    )

    if not user_info or not address_info:
        raise HTTPException(
            status_code=400, detail="بيانات المستخدم أو العنوان غير مكتملة"
        )

    total_price = price_product * order.count
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        sql.RunCode(
            "INSERT INTO orders (product_id, customer_id, customer_name, total_price, Address, Date) VALUES (?, ?, ?, ?, ?, ?)",
            (
                order.product_id,
                order.customer_id,
                user_info[0][0],
                total_price,
                address_info[0][0],
                time_now,
            ),
        )

        sql.RunCode(
            "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
            (order.count, order.product_id),
        )

        return {"Status": "Success", "Message": "تم تسجيل الطلب وتحديث المخزن بنجاح"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="حدث خطأ أثناء معالجة الطلب")

@app.get("/GetAllOrders")
async def GetAllOrders():
    result = []
    fetched_order = sql.RunCode("SELECT * FROM orders")
    num_order = len(fetched_order)
    for i in range(num_order):
        result.append(
            {
                "id": fetched_order[i][0],
                "product_id": fetched_order[i][1],
                "customer_id": fetched_order[i][2],
                "customer_name": fetched_order[i][3],
                "total_price": fetched_order[i][4],
                "Address": fetched_order[i][5],
                "Date": fetched_order[i][6],
                "status": fetched_order[i][7],
            }
        )

    return result

# ============================(Products)=======================
