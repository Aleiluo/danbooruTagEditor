import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from mainWindow import Ui_mainWindow
from interactive_events import userEvents
from file_manager import fileManager
from tag_tran import tagTran
from tagfilter import Filters

class LoadMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 载入窗口
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)


class EditorGUI(tagTran, fileManager, userEvents, Filters,
                LoadMainWindow):
    def __init__(self):
        super().__init__()

        # 表头按窗口比例等间距缩放
        self.ui.tagTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        # 加载剪贴板
        self.clipboard = QApplication.clipboard()
        # 安装事件过滤器
        self.installEventFilter(self)
        # 英文标签是否更改
        self.entagChanged = False

        # 菜单:打开文件
        self.ui.openFile.triggered.connect(self.selectFolder)
        # 菜单:促存文件
        self.ui.saveFile.triggered.connect(self.saveTags2File)
        # 菜单:保存单选功能
        self.ui.keepOrder.triggered.connect(
            lambda: self.keep1SavemodSelect("keep"))
        self.ui.sortOrder.triggered.connect(
            lambda: self.keep1SavemodSelect("sort"))
        # 菜单:打开标签过滤编辑器
        self.ui.openFilter.triggered.connect(self.open_Filter)
        # 菜单:清空过滤器
        self.ui.clearFilter.triggered.connect(self.clear_Filter)

    def keep1SavemodSelect(self, curMode):
        if curMode == "keep" and self.ui.sortOrder.isChecked():
            self.ui.sortOrder.setChecked(False)
            self.entagChanged = True
            self.windowTitlestar()
        elif curMode == "sort" and self.ui.keepOrder.isChecked():
            self.ui.keepOrder.setChecked(False)
            self.entagChanged = True
            self.windowTitlestar()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditorGUI()
    # 窗口图标
    icon = QIcon("GUI.png")
    window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec_())
