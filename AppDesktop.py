import sys, os, shutil
from PyQt5 import uic, QtWidgets
from ConnactSQL import Sql
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog, QMessageBox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database", "shop.db")

sql = Sql(pathfile=db_path)


class Clothing(QtWidgets.QWidget):
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

        self.tableWidget.itemClicked.connect(self.GetSelection)
        self.tableWidget_2.itemClicked.connect(self.GetOrderSelection)

        # Orders and Tab Interactions
        self.tabWidget.currentChanged.connect(self.OnTabChanged)

        self.LoadData()
        self.LoadOrders()
        self.show()

    def SelectImage(self):
        filePath, _ = QFileDialog.getOpenFileName(
            self,
            "Get Image file",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All files (*.*)",
        )

        if filePath:
            target_folder = "Clothings_Photo"

            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            filename = os.path.basename(filePath)

            destination_path = os.path.join(target_folder, filename)

            shutil.copy2(filePath, destination_path)

            self.lineEdit_5.setText(destination_path)

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


#==============(Orders)===============
    def OnTabChanged(self, index):
        """Refresh the active tab's data when the user switches tabs"""
        if index == 0: 
            self.LoadData()
        elif index == 1:  
            self.LoadOrders()

    def LoadOrders(self):
            """Fetch orders from the database and populate tableWidget_2"""
            self.tableWidget_2.setRowCount(0)
            query = "SELECT o.id, o.product_id ,p.name ,o.customer_name, o.total_price,o.count, o.status, o.Date, o.Address FROM orders o JOIN products  p ON o.product_id = p.id"
            results = sql.RunCode(query)
            
            if results:
                for row_number, row_data in enumerate(results):
                    self.tableWidget_2.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        self.tableWidget_2.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
                        
    def GetOrderSelection(self):
        """Fill inputs when an order is clicked in tableWidget_2"""
        row = self.tableWidget_2.currentRow()
        
        if row != -1:
            self.lineEdit_6.setText(self.tableWidget_2.item(row, 0).text())   
            self.lineEdit_7.setText(self.tableWidget_2.item(row, 1).text())   
            self.lineEdit_8.setText(self.tableWidget_2.item(row, 2).text())   
            self.lineEdit_9.setText(self.tableWidget_2.item(row, 3).text())   
            self.lineEdit_10.setText(self.tableWidget_2.item(row, 4).text())  
            self.lineEdit_11.setText(self.tableWidget_2.item(row, 5).text())
            self.lineEdit_12.setText(self.tableWidget_2.item(row, 6).text())
            self.lineEdit_13.setText(datetime.now().strftime(self.tableWidget_2.item(row, 7).text()))
            self.textEdit.setPlainText(self.tableWidget_2.item(row, 8).text())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    sql.CreateTable()
    window = Clothing()
    sys.exit(app.exec_())
