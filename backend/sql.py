import sqlite3
import os


class Sql:
    def __init__(self, pathfile: str = "./database/shop.db"):
        self.PathFile = pathfile

    def CreateTable(self):
        """ Create Table shop """
        pathf = os.path.exists(self.PathFile)
        if not pathf:
            try:
                with sqlite3.connect(self.PathFile) as conn:
                    cur = conn.cursor()
                    cur.execute("""
-- 1. جدول المنتجات
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT,
    image_url TEXT,
    stock_quantity INTEGER DEFAULT 0
);

-- 2. جدول الطلبيات
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    total_price REAL NOT NULL,
    status TEXT DEFAULT 'pending' -- (pending, shipped, delivered)
);

-- 3. جدول تفاصيل الطلبية (الرابط)
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
""")
                    conn.commit()
            except sqlite3.Error as se:
                print(f"Error Sql : {se}")

    def RunCode(self, codesql: str = "", values: tuple = ()):
        """ Run code SQL """
        try:
            with sqlite3.connect(self.PathFile) as conn:
                cur = conn.cursor()
                cur.execute(codesql, values)
                if codesql.strip().upper().startswith("SELECT"):
                    return cur.fetchall()
                conn.commit()
                return True
        except sqlite3.Error as se:
            print(f"Error sql database : {se}")
            return None
        except Exception as e:
            print(f"Error : {e}")
            return None
