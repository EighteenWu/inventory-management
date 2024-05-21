# src/ui_controller.py
import string
import random

from data_model import Part, OperationLog
from data_dao import PartDAO, OperationLogDAO
from PySide6.QtGui import QShortcut
from PySide6.QtWidgets import (QMenu, QInputDialog, QMessageBox,
                               QTableWidgetItem, QTableWidget, QFormLayout, QLineEdit, QVBoxLayout, QDialog,
                               QSizePolicy, QDialogButtonBox, QTableWidgetSelectionRange, QCheckBox, QLabel,
                               QHeaderView)
from PySide6.QtCore import Qt
from datetime import datetime


class UIController:

    def __init__(self, widget):

        self.part_dao = PartDAO()  # 创建 PartDAO 实例
        self.log_dao = OperationLogDAO()
        self.widget = widget
        self.widget.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.sort_order = {}  # 初始化排序顺序字典

        self.widget.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.widget.tableWidget.customContextMenuRequested.connect(self.create_context_menu)

        # 操作绑定
        self.widget.shortcut.activated.connect(self.on_ctrl_f_pressed)  # 快捷键触发时执行 on_ctrl_f_pressed 函数
        self.widget.drawing_number_input.returnPressed.connect(self.find_part())  # 图号输入框回车时执行 find 函数
        self.ctrl_s_shortcut = QShortcut('Ctrl+S', self.widget)
        self.ctrl_s_shortcut.activated.connect(self.commit_edit)
        self.widget.tableWidget.itemDoubleClicked.connect(self.edit_item)  # 双击表格项时执行 edit_item 函数

        # ---- 按钮操作事件
        self.widget.get_stock_b.clicked.connect(self.get_stock)  # 将获取库存按钮点击事件连接到 get_stock 函数
        # self.change_stock_b.clicked.connect(self.change_stock)
        self.widget.tableWidget.horizontalHeader().sectionClicked.connect(
            self.sort_column)  # 将表格组件水平表头点击事件连接到 sort_column 函数
        self.widget.find_b.clicked.connect(self.find_part)  # 将查找按钮点击事件连接到 find 函数
        # 将表格右击事件连接到 show_context_menu 函数
        self.widget.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        # 将新增零件按钮点击事件连接到 add_part_dialog 函数
        self.widget.add_button.clicked.connect(self.add_part_dialog)

        # ----  菜单栏函数绑定
        self.widget.clear_button.clicked.connect(self.clear_log)  # 将清除日志按钮点击事件连接到 clear_log 函数
        self.widget.batch_delete_button.clicked.connect(self.batch_delete)  # 将批量删除按钮绑定到batch_delete函数
        self.widget.batch_storage_button.clicked.connect(self.batch_storage)  # 将批量入库按钮绑定到batch_storage函数
        self.widget.batch_exit_button.clicked.connect(self.batch_out_storage)  # 将批量出库按钮绑定到batch_out_storage函数

    def add_part(self, part_data):
        # 处理添加零件的逻辑
        part = Part(**part_data)
        self.part_dao.add_part(part)

    def update_part_quantity(self, drawing_number, new_quantity):
        # 处理更新零件数量的逻辑
        self.part_dao.update_part_quantity(drawing_number, new_quantity)

    def add_operation_log(self, log_data):
        # 处理添加操作记录的逻辑
        log = OperationLog(**log_data)
        self.log_dao.add_operation_log(log)

    def get_logs_by_drawing_number(self, drawing_number):
        # 获取特定零件的操作记录
        return self.log_dao.get_logs_by_drawing_number(drawing_number)

    def delete_logs_by_drawing_number(self, drawing_number):
        # 删除特定零件的操作记录
        self.log_dao.delete_logs_by_drawing_number(drawing_number)

    # 清理日志函数
    def clear_log(self):
        self.widget.log_editor.clear()

    def add_log(self, message):
        """将日志信息添加到日志编辑器中。"""
        self.widget.log_editor.appendPlainText(message)

    # 表格数据填充函数
    def render_table(self, parts):
        self.clear_table()
        # 设置表格固定列名为: 物料编号、产品图号、产品名称、库存数量、每箱数量、最后更改时间
        column_names = ["", "物料编号", "产品图号", "产品名称", "库存数量", "每箱数量", "上次更改日期"]  # 列名列表
        self.widget.tableWidget.setColumnCount(len(column_names))
        self.widget.tableWidget.setHorizontalHeaderLabels(column_names)  # 设置表格列名

        header = self.widget.tableWidget.horizontalHeader()  # 获取表格的水平表头
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 设置第一列的宽度模式为固定
        header.resizeSection(0, 20)  # 设置第一列的宽度为50
        for i in range(1, len(column_names) - 1):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
            # header.setSectionResizeMode(i, QHeaderView.Interactive)  # 设置其他列的宽度模式为可手动拖动
        self.widget.tableWidget.setRowCount(len(parts) + 1)
        for i, part in enumerate(parts):
            checkbox = QCheckBox()
            # 复选框设置为未选中状态
            checkbox.setCheckState(Qt.Unchecked)
            # 复选框状态改变时触发 select_row 函数
            checkbox.stateChanged.connect(lambda state, row=i: self.select_row(state, row))
            # 将复选框添加到表格中
            self.widget.tableWidget.setCellWidget(i, 0, checkbox)

            self.widget.tableWidget.setItem(i, 1, QTableWidgetItem(str(part.no)))
            self.widget.tableWidget.setItem(i, 2, QTableWidgetItem(part.product_drawing_number))
            self.widget.tableWidget.setItem(i, 3, QTableWidgetItem(part.name))
            self.widget.tableWidget.setItem(i, 4, QTableWidgetItem(str(part.inventory_quantity)))
            self.widget.tableWidget.setItem(i, 5, QTableWidgetItem(str(part.quantity_per_carton)))
            self.widget.tableWidget.setItem(i, 6, QTableWidgetItem(part.update_time.strftime("%Y-%m-%d")))

    def render_log_table(self, log):
        self.clear_table()
        # 重新设置表格列名
        self.widget.tableWidget.setHorizontalHeaderLabels(
            ["时间", "产品图号", "操作类型", "操作字段", "更改前值", "更改后值"])
        # 重新设置第一列宽度为自适应
        self.widget.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # 设置表格行数
        self.widget.tableWidget.setRowCount(len(log))

        for i, log in enumerate(log):
            self.widget.tableWidget.setItem(i, 0, QTableWidgetItem(str(log.time)))
            self.widget.tableWidget.setItem(i, 1, QTableWidgetItem(log.product_drawing_number))
            self.widget.tableWidget.setItem(i, 2, QTableWidgetItem(log.operator_type))
            self.widget.tableWidget.setItem(i, 3, QTableWidgetItem(log.operator_fields))
            self.widget.tableWidget.setItem(i, 4, QTableWidgetItem(log.value_before_change))
            self.widget.tableWidget.setItem(i, 5, QTableWidgetItem(log.changed_value))

    def select_row(self, state, row):
        if state == Qt.Checked:
            self.widget.tableWidget.selectRow(row)
        else:
            self.widget.tableWidget.setRangeSelected(
                QTableWidgetSelectionRange(row, 0, row, self.widget.tableWidget.columnCount() - 1), False)

    def context_menu(self, event):
        self.create_context_menu(event)

    def create_context_menu(self, position):

        self.context_menu = QMenu(self.widget.tableWidget)  # 创建右键菜单

        # 创建菜单项
        out_stock_action = self.context_menu.addAction("出库")
        in_stock_action = self.context_menu.addAction("入库")
        edit_action = self.context_menu.addAction("编辑")
        delete_action = self.context_menu.addAction("删除")
        add_action = self.context_menu.addAction("查询操作日志")

        # 连接菜单项的触发信号到相应的槽函数
        out_stock_action.triggered.connect(self.out_stock)
        in_stock_action.triggered.connect(self.in_stock)
        edit_action.triggered.connect(self.edit_part)
        delete_action.triggered.connect(self.delete_part)
        add_action.triggered.connect(self.query_operate_log)

        # 将菜单项添加到右键菜单
        self.context_menu.addAction(out_stock_action)
        self.context_menu.addAction(in_stock_action)
        self.context_menu.addAction(edit_action)
        self.context_menu.addAction(delete_action)
        self.context_menu.addAction(add_action)

        # 在鼠标点击的位置显示右键菜单
        self.context_menu.exec_(self.widget.tableWidget.viewport().mapToGlobal(position))

    def query_operate_log(self):
        """
        查询操作日志
        :return:
        """
        # 1、获取当前选中行的图号
        selected_rows = self.widget.tableWidget.selectedItems()
        if len(selected_rows) == 0:
            QMessageBox.warning(self.widget, "警告", "请先选择要查询的零件")
            return
        drawing_number = selected_rows[1].text()
        # 2、获取该图号的操作日志
        logs = self.get_logs_by_drawing_number(drawing_number)
        # 3、将操作日志重新渲染在表格组件当中,重写render_table函数
        self.render_log_table(logs)

    def out_stock(self):
        # 出库操作
        # 点击出库按钮时,获取表格当前行所有数据,弹出输入框,输入出库数量
        selected_rows = self.widget.tableWidget.selectedItems()
        if len(selected_rows) == 0:
            QMessageBox.warning(self.widget, "警告", "请先选择要出库的零件")
            return
        drawing_number = selected_rows[1].text()
        before_part = self.part_dao.get_part_by_drawing_number(drawing_number)
        quantity = QInputDialog.getInt(self.widget, "出库", f"请输入{drawing_number}出库数量")
        if quantity[1]:
            # 出库操作为减少库存数量
            self.update_part_quantity(drawing_number, before_part.inventory_quantity - quantity[0])
            self.add_log(f"出库了{quantity[0]}个{before_part.name}零件")
            self.find_part()

    def in_stock(self):
        # 入库操作
        # 点击入库按钮时，获取当前选中的行,并获取选中行的图号,弹出输入框,输入入库数量
        # 选择这一行所有的值
        selected_rows = self.widget.tableWidget.selectedItems()
        if len(selected_rows) == 0:
            QMessageBox.warning(self.widget, "警告", "请先选择要入库的零件")
            return
        drawing_number = selected_rows[1].text()
        name = selected_rows[2].text()
        old_quantity = int(selected_rows[3].text())
        quantity = QInputDialog.getInt(self.widget, "入库", f"请输入{drawing_number}入库数量")
        if quantity[1]:
            self.update_part_quantity(drawing_number, old_quantity + quantity[0])
            self.add_log(f"入库了{quantity[0]}个{name}零件")
            self.find_part()

    def edit_part(self):
        # 弹出新对话框, 新对话框中显示选中行的数据,并可以修改
        selected_rows = self.widget.tableWidget.selectedItems()
        if len(selected_rows) == 0:
            QMessageBox.warning(self.widget, "警告", "请先选择要编辑的零件")
            return
        drawing_number = selected_rows[1].text()
        # 根据图号获取零件信息
        part = self.part_dao.get_part_by_drawing_number(drawing_number)
        q_dialog = EditPartDialog(part, self.widget, self)
        # 展示对话框
        q_dialog.exec_()

    def edit_item(self, item):
        # 单元格编辑操作
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        index = self.widget.tableWidget.indexFromItem(item)
        self.widget.tableWidget.edit(index)

    def commit_edit(self):
        item = self.widget.tableWidget.currentItem()
        self.update_item(item)

    def update_item(self, item):
        row = item.row()
        column = item.column()
        new_value = item.text()

        # 获取需要更新的零件的图号
        drawing_number = self.widget.tableWidget.item(row, 2).text()
        # 根据列号确定需要更新的字段
        if column == 3:  # 假设名称在第4列
            field = 'name'
        elif column == 4:  # 假设库存数量在第5列
            field = 'inventory_quantity'
        elif column == 5:  # 假设每箱数量在第6列
            field = 'quantity_per_carton'
        else:
            return  # 如果不是这些列，不进行更新

        # 更新数据库
        part = self.part_dao.get_part_by_drawing_number(drawing_number)
        if part:
            setattr(part, field, new_value)
            self.part_dao.update_part(part)
            self.add_log(f"更新了{drawing_number}零件的{field}为{new_value}")

    def delete_part(self):
        # 处理删除零件的逻辑
        selected_rows = self.widget.tableWidget.selectedItems()
        if len(selected_rows) == 0:
            QMessageBox.warning(self.widget, "警告", "请先选择要编辑的零件")
            return
        drawing_number = selected_rows[1].text()
        # 根据图号获取零件信息
        part = self.part_dao.get_part_by_drawing_number(drawing_number)
        # 弹出是否确认删除的对话框
        reply = QMessageBox.question(self.widget, 'Message', f'删除零件: {part.name}?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.add_log(f'删除图号为: {drawing_number},name: {part.name}')
            self.part_dao.delete_part_by_drawing_number(drawing_number)
            self.find_part()
        else:
            return

    def add_part(self):
        # 添加操作
        pass

    # 表格数据清空函数
    def clear_table(self):
        self.widget.tableWidget.setRowCount(0)

    # 获取所有数据函数
    def get_stock(self):
        # 关联data_dao内的query_all_data函数，并将查询到的数据渲染到表格中
        parts = self.part_dao.query_all_data()
        self.render_table(parts)

    def find_part(self):
        """
        查找函数,支持根据图号,产品名称查找数据
        :return:
        """
        drawing_number, name, start_time, end_time = self.get_query_condition()
        parts = self.part_dao.query_data_by_condition(drawing_number, name, start_time, end_time, self.add_log)
        self.add_log(
            f"查询了图号为{drawing_number},名称为{name}的零件,起止时间为{start_time}到{end_time}的零件信息,共{len(parts)}条数据")
        self.render_table(parts)

    def on_ctrl_f_pressed(self):
        # 获取光标并清除内容
        self.widget.drawing_number_input.setFocus(Qt.ActiveWindowFocusReason)
        self.widget.drawing_number_input.clear()

    # 字段排序函数
    def sort_column(self, index):
        # 获取当前列引用
        header = self.widget.tableWidget.horizontalHeaderItem(index).text()

        # 获取排序顺序
        sort_order = self.sort_order.get(header, Qt.AscendingOrder)
        self.sort_order[header] = Qt.DescendingOrder if sort_order == Qt.AscendingOrder else Qt.AscendingOrder

        # 排序数据
        self.widget.tableWidget.sortItems(index, self.sort_order[header])

    # 条件查询函数
    def get_query_condition(self):
        drawing_number = self.widget.drawing_number_input.text()
        name = self.widget.name_input.text()
        start_time = self.widget.start_time_input.date().toPython()
        end_time = self.widget.end_time_input.date().toPython()
        return drawing_number, name, start_time, end_time

    # 批量删除函数
    def batch_delete(self):
        """
        批量删除函数,根据用户选择的行删除数据
        :return:
        """
        # 获取选中的行的图号
        drawing_numbers = set()
        for i in range(self.widget.tableWidget.rowCount()):
            checkbox = self.widget.tableWidget.cellWidget(i, 0)
            if checkbox is not None and checkbox.isChecked():
                drawing_number = self.widget.tableWidget.item(i, 2).text()
                drawing_numbers.add(drawing_number)

        if not drawing_numbers:
            # 弹出警告框
            QMessageBox.warning(self.widget, "警告", "请先选择要批量删除的零件")
            return

        # 弹出确认框
        reply = QMessageBox.question(self.widget, "警告", "是否删除选中的零件?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        # 删除选中的行
        self.part_dao.batch_delete(drawing_numbers, self.add_log)
        self.find_part()

    # 弹出新增零件对话框,对话框包括产品图号,产品名称,库存数量,每箱数量
    def add_part_dialog(self):
        q_dialog = AddPartDialog(self.widget, self)
        q_dialog.exec_()

    def batch_storage(self):
        # 获取选中的行的图号
        drawing_numbers = set()
        for i in range(self.widget.tableWidget.rowCount()):
            checkbox = self.widget.tableWidget.cellWidget(i, 0)
            if checkbox is not None and checkbox.isChecked():
                drawing_number = self.widget.tableWidget.item(i, 2).text()
                drawing_numbers.add(drawing_number)

        if not drawing_numbers:
            # 弹出警告框
            QMessageBox.warning(self.widget, "警告", "请先选择要批量入库的零件")
            return

        parts = [self.part_dao.get_part_by_drawing_number(drawing_number) for drawing_number in drawing_numbers]

        dialog = BatchStorageDialog(parts, self.widget)
        if dialog.exec_() == QDialog.Accepted:
            quantities = dialog.get_values()
            for part, quantity in zip(parts, quantities):
                self.update_part_quantity(part.product_drawing_number, part.inventory_quantity + int(quantity))
                self.add_log(f"入库了 {quantity} 个 {part.product_drawing_number} 零件")
            self.find_part()

    def batch_out_storage(self):
        """
        批量出库
        :return:
        """
        # 获取选中的行的图号
        drawing_numbers = set()
        for i in range(self.widget.tableWidget.rowCount()):
            checkbox = self.widget.tableWidget.cellWidget(i, 0)
            if checkbox is not None and checkbox.isChecked():
                drawing_number = self.widget.tableWidget.item(i, 2).text()
                drawing_numbers.add(drawing_number)

        if not drawing_numbers:
            # 弹出警告框
            QMessageBox.warning(self.widget, "警告", "请先选择要批量出库的零件")
            return

        parts = [self.part_dao.get_part_by_drawing_number(drawing_number) for drawing_number in drawing_numbers]

        dialog = BatchOutStorageDialog(parts, self.widget)
        if dialog.exec_() == QDialog.Accepted:
            quantities = dialog.get_values()
            for part, quantity in zip(parts, quantities):
                self.update_part_quantity(part.product_drawing_number, part.inventory_quantity - int(quantity))
                self.add_log(f"出库了 {quantity} 个 {part.product_drawing_number} 零件")
            self.find_part()


class EditPartDialog(QDialog, UIController):
    def __init__(self, part: Part, parent=None, ui_controller=None):
        super().__init__(parent)
        self.widget = parent
        self.ui_controller = ui_controller
        self.part_dao = PartDAO()  # 创建 PartDAO 实例

        self.setWindowTitle("编辑零件")

        # 窗口自适应大小
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.layout = QVBoxLayout(self)

        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        self.no_input = QLineEdit(str(part.no))
        self.no_input.setReadOnly(True)
        self.form_layout.addRow("物料编号", self.no_input)

        self.drawing_number_input = QLineEdit(part.product_drawing_number)
        self.drawing_number_input.setReadOnly(True)
        self.form_layout.addRow("产品图号", self.drawing_number_input)

        self.name_input = QLineEdit(part.name)
        self.form_layout.addRow("产品名称", self.name_input)

        self.inventory_quantity_input = QLineEdit(str(part.inventory_quantity))
        self.form_layout.addRow("库存数量", self.inventory_quantity_input)

        self.quantity_per_carton_input = QLineEdit(str(part.quantity_per_carton))
        self.form_layout.addRow("每箱数量", self.quantity_per_carton_input)

        # 对话框添加确定按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.layout.addWidget(self.button_box)

        # 确定按钮绑定更新函数
        self.button_box.accepted.connect(self.update_part)
        # 取消按钮绑定关闭函数
        self.button_box.rejected.connect(self.close)

    def update_part(self):
        updated_part = self.get_updated_part()
        part = Part(**updated_part)
        self.part_dao.update_part(part)
        # 日志输出更改信息,包括图号,名称,库存数量,每箱数量,原来的数据和更新后的数据
        self.add_log(f"更新了{part.name}零件,更新后数据为{part.__str__()}")
        # 添加更新日期，图号，操作类型，更改字段，更改前值，更改后值

        self.find_part()
        # 关闭对话框
        self.close()

    def get_updated_part(self):
        return {
            "no": self.no_input.text(),
            "product_drawing_number": self.drawing_number_input.text(),
            "name": self.name_input.text(),
            "inventory_quantity": int(self.inventory_quantity_input.text()),
            "quantity_per_carton": int(self.quantity_per_carton_input.text())
        }


class AddPartDialog(QDialog, UIController):
    def __init__(self, parent=None, ui_controller=None):
        super().__init__(parent)
        self.widget = parent
        self.ui_controller = ui_controller
        self.part_dao = PartDAO()  # 创建 PartDAO 实例
        self.log_dao = OperationLogDAO()

        self.setWindowTitle("新增零件")

        # 窗口自适应大小
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.layout = QVBoxLayout(self)

        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        self.id_input = QLineEdit()
        self.form_layout.addRow("物料编号", self.id_input)

        self.drawing_number_input = QLineEdit()
        self.form_layout.addRow("产品图号", self.drawing_number_input)

        self.name_input = QLineEdit()
        self.form_layout.addRow("产品名称", self.name_input)

        self.inventory_quantity_input = QLineEdit()
        self.form_layout.addRow("库存数量", self.inventory_quantity_input)

        self.quantity_per_carton_input = QLineEdit()
        self.form_layout.addRow("每箱数量", self.quantity_per_carton_input)

        # 对话框添加确定按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.layout.addWidget(self.button_box)

        # 确定按钮绑定添加函数
        self.button_box.accepted.connect(self.add_part)
        # 取消按钮绑定关闭函数
        self.button_box.rejected.connect(self.close)

    def add_part(self):
        new_part = self.get_new_part()
        part = Part(**new_part)
        self.part_dao.add_part(part)
        # 日志输出新增信息,包括图号,名称,库存数量,每箱数量
        self.add_log(f"新增了{new_part['name']}零件,数据为{new_part}")
        self.find_part()
        # 关闭对话框
        self.close()

    def get_new_part(self):
        return {
            "no": int(self.id_input.text()),  # 物料编号
            "product_drawing_number": self.drawing_number_input.text(),
            "name": self.name_input.text(),
            "inventory_quantity": int(self.inventory_quantity_input.text()),
            "quantity_per_carton": int(self.quantity_per_carton_input.text()),
            # 1组固定值为0
            "a_group_total": 0,
            # 2组固定值为0
            "b_group_total": 0,
            # 上次更改日期默认为当前日期
            "update_time": datetime.now().strftime("%Y-%m-%d"),
            # id:00001c1f41af455d92c8fe2ced77a106359 随机生成35数字小写字母混合
            "id": ''.join(random.choices(string.ascii_lowercase + string.digits, k=35))
        }


class BatchStorageDialog(QDialog):
    def __init__(self, parts, parent=None):
        super().__init__(parent)
        self.parts = parts
        self.setWindowTitle("批量入库")

        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        self.inputs = []
        for part in parts:
            label = QLabel(f"请输入 {part.name} 入库数量")
            input_field = QLineEdit()
            self.inputs.append(input_field)
            self.form_layout.addRow(label, input_field)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def get_values(self):
        return [input_field.text() for input_field in self.inputs]


class BatchOutStorageDialog:
    def __init__(self, parts, parent=None):
        self.parts = parts
        self.dialog = QDialog(parent)
        self.dialog.setWindowTitle("批量出库")

        self.layout = QVBoxLayout(self.dialog)
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        self.inputs = []
        for part in parts:
            label = QLabel(f"请输入 {part.name} 出库数量")
            input_field = QLineEdit()
            self.inputs.append(input_field)
            self.form_layout.addRow(label, input_field)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.dialog.accept)
        self.button_box.rejected.connect(self.dialog.reject)

    def exec_(self):
        return self.dialog.exec_()

    def get_values(self):
        return [input_field.text() for input_field in self.inputs]
