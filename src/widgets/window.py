from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import (QDateEdit, QLineEdit, QLabel,
                               QPushButton, QVBoxLayout, QWidget,
                               QMenu, QInputDialog, QMessageBox,
                               QTableWidgetItem, QTableWidget, QPlainTextEdit, QHBoxLayout, QSplitter, QHeaderView,
                               QCheckBox)
from PySide6.QtCore import QDate, Qt
from datetime import datetime, timedelta


class Widget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sort_order = {}  # 初始化排序顺序字典

        # ---- 创建布局
        self.v_layout = QVBoxLayout()  # 创建垂直布局
        self.h_layout = QHBoxLayout()  # 创建水平布局
        self.e_layout = QHBoxLayout()  # 创建底部按钮布局
        self.left_right_layout = QHBoxLayout()  # 创建左右布局
        # self.v_layout.addLayout(self.h_layout1)

        self.setWindowTitle('库存管理系统')  # 设置窗口标题
        self.resize(1000, 600)  # 设置窗口大小
        self.label = QLabel('库存查询:')  # 创建标签“库存查询”
        self.get_stock_b = QPushButton("查询全部")  # 创建按钮“查询全部”
        # ---- 组件创建

        self.tableWidget = QTableWidget()  # 创建表格控件
        self.tableWidget.verticalHeader().setVisible(False)  # 隐藏表格垂直表头
        self.tableWidget.horizontalHeader().setHighlightSections(False)  # 取消选中行高亮
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)  # 设置表格不可编辑


        # 创建一个文本编辑器来显示日志信息
        self.log_editor = QPlainTextEdit("日志输出:")
        self.log_editor.setReadOnly(True)  # 设置只读

        # 创建分隔器
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.tableWidget)
        self.splitter.addWidget(self.log_editor)

        # 创建右键菜单
        self.context_menu = QMenu(self)

        self.drawing_number_label = QLabel('图号:')  # 创建标签“图号”
        self.drawing_number_input = QLineEdit()  # 创建输入框
        self.name_label = QLabel('产品名称:')  # 创建产品名称输入框
        self.name_input = QLineEdit()  # 创建产品名称输入框
        self.update_label = QLabel('最后更改时间介于:')  # 创建标签“最后更改时间介于”

        self.start_time_input = QDateEdit()  # 创建日期编辑器
        self.start_time_input.setCalendarPopup(True)
        self.start_time_input.setDisplayFormat("yyyy-MM-dd")
        # self.start_time_input.setDate(QDate.currentDate().addDays(-30))  # 设置默认开始时间为30天前
        self.start_time_input.setDate((datetime.now() - timedelta(days=30)).date())

        self.end_time_input = QDateEdit()  # 创建日期编辑器
        self.end_time_input.setCalendarPopup(True)
        self.end_time_input.setDisplayFormat("yyyy-MM-dd")
        self.end_time_input.setDate(datetime.now().date())  # 设置默认结束时间为当前时间

        # self.update_dates()  # 更新日期

        self.find_b = QPushButton("条件查询")  # 创建按钮“条件查询”

        # ---- 菜单栏按钮创建
        self.add_button = QPushButton("新增零件")
        self.batch_delete_button = QPushButton("批量删除")
        self.batch_storage_button = QPushButton("批量入库")
        self.batch_exit_button = QPushButton("批量出库")
        self.clear_button = QPushButton("清除日志")

        # ----查询栏按钮添加到查询div中
        self.h_layout.addWidget(self.label)  # 添加“库存查询”标签到布局
        self.h_layout.addWidget(self.get_stock_b)  # 添加“查询全部”按钮到布局
        self.h_layout.addSpacing(50)  # 添加间隔
        self.h_layout.addWidget(self.drawing_number_label)  # 添加“图号”标签到布局
        self.h_layout.addWidget(self.drawing_number_input)  # 添加图号输入框到布局
        self.h_layout.addWidget(self.name_label)  # 添加产品名称标签到布局
        self.h_layout.addWidget(self.name_input)  # 添加产品名称输入框到布局
        self.h_layout.addWidget(self.update_label)  # 添加“最后更改时间介于”标签到布局
        self.h_layout.addWidget(self.start_time_input)  # 添加开始日期编辑器到布局
        self.h_layout.addWidget(self.end_time_input)  # 添加结束日期编辑器到布局
        self.h_layout.addWidget(self.find_b)  # 添加“条件查询”按钮到布局

        # ----列表明细和日志窗口添加到中间div中
        self.left_right_layout.addWidget(self.splitter)  # 添加分隔器到左右布局

        # ----菜单栏按钮添加到底部水平div中
        self.e_layout.addWidget(self.add_button)  # 添加日志清理按钮
        self.e_layout.addWidget(self.batch_delete_button)  # 添加批量删除按钮
        self.e_layout.addWidget(self.batch_exit_button)  # 添加批量出库按钮
        self.e_layout.addWidget(self.batch_storage_button)  # 添加批量入库按钮
        self.e_layout.addWidget(self.clear_button)  # 添加日志清楚按钮

        # ----整体布局添加到主布局和主窗口
        self.v_layout.addLayout(self.h_layout)  # 添加水平布局到垂直布局
        self.v_layout.addLayout(self.left_right_layout)  # 添加左右布局到垂直布局
        self.v_layout.addLayout(self.e_layout)  # 添加底部水平布局到垂直布局
        self.setLayout(self.v_layout)  # 设置布局到窗口

        # ----快捷键设置
        self.shortcut = QShortcut(QKeySequence("Ctrl+F"), self)  # 设置快捷键 Ctrl+F
