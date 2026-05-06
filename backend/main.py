from fastapi import FastAPI
from ConnactSQL import Sql
from models import UserRegistration
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "..", "database", "shop.db")

app = FastAPI(description="""This Project About Clothing Store""", version="1.0.0")
sql = Sql(db_path)


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


@app.post("/Signup")
async def signup (NewUser: UserRegistration):
    ...
