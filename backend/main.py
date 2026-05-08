from fastapi import FastAPI, HTTPException, status
from ConnactSQL import Sql
from backend.models import UserRegistration, OrderCreate, InfoUser, UserLogin
import os
import sys
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "..", "database", "shop.db")

app = FastAPI(description="""This Project About Clothing Store""", version="1.0.0")
sql = Sql(db_path)


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
        result.append(
            {
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "password": row[3],
                "info": {
                    "image": row[4],
                    "phone": row[5],
                    "Address": row[6],
                },
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


@app.get("/", description="""Get All Data about Clothing""")
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
                "image": fetched_product[i][4],
            }
        )

    return result
