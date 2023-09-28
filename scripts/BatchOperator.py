from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from ui.BatchOperatorWindow import Ui_BatchOperator


class BatchOperator:
    def __init__(self):
        super().__init__()
        # 载入子窗口
        self.batch_operator = QWidget()
        self.batch_operator.ui = Ui_BatchOperator()
        self.batch_operator.ui.setupUi(self.batch_operator)

        # Ctrl+Enter:执行批量添加
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Enter), self.batch_operator) \
            .activated.connect(self.batch_add)
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Return), self.batch_operator) \
            .activated.connect(self.batch_add)
        # Ctrl+Del:执行批量删除
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Delete), self.batch_operator) \
            .activated.connect(self.batch_del)
        # Ctrl+Z:撤销操作
        # 懒得做
        # Ctrl+Y:重做
        # 懒得做
        # 批处理:批量增加
        self.batch_operator.ui.batchAdd.clicked.connect(self.batch_add)
        # 批处理:批量删除
        self.batch_operator.ui.batchDel.clicked.connect(self.batch_del)
        # 批处理:插入模式改变
        self.batch_operator.ui.buttonGroup.buttonToggled.connect(self.batch_modeChanged)


