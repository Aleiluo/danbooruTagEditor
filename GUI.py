import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from ui.MainWindow import Ui_mainWindow
from scripts.UserEvents import UserEvents
from scripts.FileManager import FileManager
from scripts.TagTran import TagTran
from scripts.TagFilter import TagFilter
from scripts.WorkingFlow import WorkingFlow
from scripts.TagCompleter import TagCompleter
from scripts.BatchOperator import BatchOperator

# TODO：两个table之间的比例可以改变
# TODO：移除无用的复制粘贴列表，换做过滤器和批量增删


class LoadMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 载入窗口
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)


class EditorGUI(TagTran, BatchOperator, WorkingFlow, TagFilter,
                UserEvents, FileManager, LoadMainWindow):
    def __init__(self):
        super().__init__()
        # 注入tag自动补全功能
        comp_words = [f'{word} ({self.translateDict[word][0]})' for word in self.translateDict.keys()]
        self.ui.tagTable.setItemDelegate(TagCompleter(self, comp_words))
        self.filter_window.ui.filtertable.setItemDelegate(TagCompleter(self, comp_words))
        self.workingflow_window.ui.wf_table.setItemDelegate(TagCompleter(self, comp_words))
        # 解锁列宽
        self.ui.tagTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.Interactive)
        # 安装事件过滤器
        self.installEventFilter(self)
        self.workingflow_window.installEventFilter(self)
        # 英文标签是否更改
        self.entagChanged = False
        # 创建撤销栈
        self.undoStack = QUndoStack(self)
        # 菜单:文件:打开文件
        self.ui.openFile.triggered.connect(self.selectFolder)
        # 菜单:文件:保存文件
        self.ui.saveFile.triggered.connect(self.saveTags2File)
        # 菜单:设置:保存模式
        self.ui.oriorder_front.triggered.connect(
            lambda: self.keep1SavemodSelect(0))
        self.ui.oriorder_behind.triggered.connect(
            lambda: self.keep1SavemodSelect(1))
        self.ui.sortorder.triggered.connect(
            lambda: self.keep1SavemodSelect(2))
        # 菜单:工具:打开标签过滤编辑器
        self.ui.openFilter.triggered.connect(self.open_Filter)
        # 菜单:工具:打开工作流
        self.ui.openWorkingFlow.triggered.connect(self.open_WorkingFlow)
        # 菜单:工具:批量操作
        self.ui.openBatchOperation.triggered.connect(self.open_BatchOperation)

        # 常量：前插
        self.front_const = -100
        # 常量：后插
        self.behind_const = 1145141919810
        # 常量：排序
        self.sort_const = -1

    def keep1SavemodSelect(self, curMode):
        self.ui.oriorder_front.setChecked(False)
        self.ui.oriorder_behind.setChecked(False)
        self.ui.sortorder.setChecked(False)
        if curMode == 0:
            # 前插模式
            self.ui.oriorder_front.setChecked(True)
        elif curMode == 1:
            # 后插模式
            self.ui.oriorder_behind.setChecked(True)
        elif curMode == 2:
            # 排序模式
            self.ui.sortorder.setChecked(True)
        # 更改index
        self.changeTagTableIndex(curMode)
        # 设置为需要保存
        self.setneedSave()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditorGUI()
    # 窗口图标
    icon = QIcon("GUI.png")
    window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec_())
