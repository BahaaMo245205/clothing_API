import sys, os ,shutil
from PyQt5 import uic, QtWidgets
from Help import Sql
from PyQt5.QtWidgets import QFileDialog, QMessageBox

sql = Sql()


class Prog(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(os.path.join(base_dir, "UI", "untitled.ui"), self)

        # Button Connections
        self.pushButton.clicked.connect(self.SelectImage)  # Choice Image
        self.pushButton_2.clicked.connect(self.AddProduct)  # Add
        self.pushButton_3.clicked.connect(self.UpdateProduct)  # Update
        self.pushButton_4.clicked.connect(self.RemoveProduct)  # Remove
        self.pushButton_5.clicked.connect(self.ClearInputs)  # Clear

        # Table Interactions
        self.tableWidget.itemClicked.connect(self.GetSelection)

        self.LoadData()
        self.show()
        
    def SelectImage(self):
        filePath, _ = QFileDialog.getOpenFileName(
            self,
            "Get Image file",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All files (*.*)",
        )
        
        if filePath:
            # 1. تحديد اسم الفولدر اللي عايز تحفظ فيه الصور
            target_folder = "Employee_Photos"
            
            # 2. التأكد إن الفولدر موجود، لو مش موجود هيعمله
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            
            # 3. الحصول على اسم الملف الأصلي (عشان نحفظه بنفس الاسم)
            filename = os.path.basename(filePath)
            
            # 4. تحديد المسار الجديد للملف
            destination_path = os.path.join(target_folder, filename)
            
            # 5. نسخ الملف
            # ملاحظة: shutil.copy2 بيحافظ على بيانات الملف الأصلية
            shutil.copy2(filePath, destination_path)
            
            # 6. تحديث الـ lineEdit بالمسار الجديد أو اسم الملف
            self.lineEdit_5.setText(destination_path)
            print(f"تم حفظ الصورة بنجاح في: {destination_path}")
    def ClearInputs(self):
        self.lineEdit.clear()  # ID
        self.lineEdit_2.clear()  # Name
        self.lineEdit_3.clear()  # Price
        self.lineEdit_4.clear()  # Stock
        self.lineEdit_5.clear()  # Image path
        self.plainTextEdit.clear()  # Description

    def LoadData(self):
        """Refresh the product table"""
        self.tableWidget.setRowCount(0)
        results = sql.RunCode(
            "SELECT id, name, price, stock_quantity, description FROM products"
        )
        if results:
            for row_number, row_data in enumerate(results):
                self.tableWidget.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.tableWidget.setItem(
                        row_number, column_number, QtWidgets.QTableWidgetItem(str(data))
                    )

    def GetSelection(self):
        """Fill inputs when a row is clicked"""
        row = self.tableWidget.currentRow()
        item = self.tableWidget.item(row, 0)
        if row != -1 and item is not None:
            product_id = item.text()
            self.lineEdit.setText(product_id)
            self.lineEdit_2.setText(self.tableWidget.item(row, 1).text())
            self.lineEdit_3.setText(self.tableWidget.item(row, 2).text())
            self.lineEdit_4.setText(self.tableWidget.item(row, 3).text())
            self.plainTextEdit.setPlainText(self.tableWidget.item(row, 4).text())

            res = sql.RunCode(
                "SELECT image_url FROM products WHERE id=?", (product_id,)
            )
            if res and res[0][0]:
                self.lineEdit_5.setText(res[0][0])
            else:
                self.lineEdit_5.clear()

    def AddProduct(self):
        name = self.lineEdit_2.text().strip()
        price = self.lineEdit_3.text().strip()
        stock = self.lineEdit_4.text().strip()
        img = self.lineEdit_5.text().strip()
        desc = self.plainTextEdit.toPlainText().strip()

        if not (name and price):
            return QMessageBox.warning(
                self, "Input Error", "Name and Price are required fields."
            )

        try:
            # Ensure numeric integrity
            price_val = float(price)
            stock_val = int(stock) if stock else 0
        except ValueError:
            return QMessageBox.warning(
                self,
                "Input Error",
                "Price must be numeric and Stock must be an integer.",
            )

        success = sql.RunCode(
            "INSERT INTO products (name, price, description, image_url, stock_quantity) VALUES (?, ?, ?, ?, ?)",
            (name, price_val, desc, img, stock_val),
        )

        if success:
            self.ClearInputs()
            self.LoadData()
            QMessageBox.information(self, "Success", "Product added successfully.")

    def UpdateProduct(self):
        product_id = self.lineEdit.text()
        if not product_id:
            return QMessageBox.warning(
                self, "Selection", "Please select a product from the table first."
            )

        name = self.lineEdit_2.text().strip()
        price = self.lineEdit_3.text().strip()
        stock = self.lineEdit_4.text().strip()
        img = self.lineEdit_5.text().strip()
        desc = self.plainTextEdit.toPlainText().strip()

        try:
            price_val = float(price)
            stock_val = int(stock) if stock else 0
        except ValueError:
            return QMessageBox.warning(
                self,
                "Input Error",
                "Price must be numeric and Stock must be an integer.",
            )

        success = sql.RunCode(
            "UPDATE products SET name=?, price=?, description=?, image_url=?, stock_quantity=? WHERE id=?",
            (name, price_val, desc, img, stock_val, product_id),
        )

        if success:
            self.LoadData()
            QMessageBox.information(self, "Success", "Product updated.")

    def RemoveProduct(self):
        product_id = self.lineEdit.text()
        if product_id:
            sql.RunCode("DELETE FROM products WHERE id=?", (product_id,))
            self.ClearInputs()
            self.LoadData()
            QMessageBox.information(self, "Success", "Product removed.")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    sql.CreateTable()
    window = Prog()
    sys.exit(app.exec_())
