import sys
from PySide6.QtWidgets import QApplication
from widgets.window import Widget
from ui_controller import UIController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    ui_controller = UIController(widget)
    widget.show()
    sys.exit(app.exec())
