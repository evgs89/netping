
from PyQt5 import QtWidgets
from ui.netPing import MainWindow
import sys

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    d_size = app.desktop().screenGeometry(app.desktop().primaryScreen()).size()
    ui = MainWindow()
    ui.move((d_size.width() - 300), 70)
    ui.show()
    sys.exit(app.exec_())
