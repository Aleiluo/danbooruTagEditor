import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from ui.MainWindow import Ui_mainWindow
from scripts.interactive_events import userEvents
from scripts.file_manager import fileManager
from scripts.tag_tran import tagTran
from scripts.tag_filter import Filters
from scripts.working_flow import workingFlow
from scripts.tag_completer import TagCompleter

# TODO：保存工作状态逻辑变更为：图片标签保存后，而不是切换图片
# TODO：批量增删功能
# TODO：增加括号是否使用转义符号'\('或'\)'
# TODO：移除无用的复制粘贴列表，换做过滤器和批量增删

class LoadMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 载入窗口
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)


class EditorGUI(tagTran, workingFlow, Filters,
                userEvents, fileManager, LoadMainWindow):
    def __init__(self):
        super().__init__()
        # 注入tag自动补全功能
        comp_words = [f'{word} ({self.translateDict[word][0]})' for word in self.translateDict.keys()]
        self.ui.tagTable.setItemDelegate(TagCompleter(self, comp_words))
        self.filter_window.ui.filtertable.setItemDelegate(TagCompleter(self, comp_words))
        self.workingflow_window.ui.wf_table.setItemDelegate(TagCompleter(self, comp_words))
        # 先等比分配，然后解锁列表宽度
        self.setEqualColumnWidth()
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

        # 常量：前插
        self.front_const = -100
        # 常量：后插
        self.behind_const = 1145141919810
        # 常量：排序
        self.sort_const = -1

    def setEqualColumnWidth(self):
        # 获取表头
        header = self.ui.tagTable.horizontalHeader()
        # 获取列数
        column_count = header.count()
        # 获取水平布局的比例
        stretchs = [self.ui.horizontalLayout.stretch(i) for i in range(3)]
        # 获取表格宽度
        table_width = self.width() * stretchs[1] / sum(stretchs)        # 计算平均宽度
        if column_count > 0:
            average_width = int(table_width / column_count) - 10
        else:
            average_width = 100  # 设置一个默认宽度
        # 设置每一列的宽度为平均宽度
        for i in range(column_count):
            header.resizeSection(i, average_width)

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
