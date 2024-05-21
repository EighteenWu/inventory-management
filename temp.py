from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QCheckBox

app = QApplication([])

# 创建主窗口
main_window = QWidget()
main_layout = QVBoxLayout(main_window)

# 创建表格组件
table_widget = QTableWidget(5, 2)  # 5行2列
table_widget.setHorizontalHeaderLabels(['Name', 'Selected'])

# 添加包含复选框的自定义单元格
for row in range(5):
    name_item = QTableWidgetItem(f'Item {row + 1}')
    table_widget.setItem(row, 0, name_item)

    checkbox = QCheckBox()
    checkbox.setChecked(False)
    table_widget.setCellWidget(row, 1, checkbox)

main_layout.addWidget(table_widget)

main_window.show()

app.exec()
