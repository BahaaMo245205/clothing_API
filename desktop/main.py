from PyQt5 import uic, QtWidgets, QtCore, QtGui
import sys


class Prog(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("./desktop/UI/untitled.ui", self)
        self.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Prog()
    sys.exit(app.exec_())
