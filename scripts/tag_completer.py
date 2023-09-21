from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class TagCompleter(QStyledItemDelegate):
    def __init__(self, parent, comp_words):
        super().__init__(parent)
        self.comp_words = comp_words
        self.CompActivated = False
        self.maxShowNumber = 7

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        comp_ListView = CustomListView()
        completer = CustomCompleter(self.comp_words, self.maxShowNumber, comp_ListView)
        editor.setCompleter(completer)
        completer.activated.connect(self.onCompleterActivated)
        return editor

    def onCompleterActivated(self):
        # 当补全项被鼠标点击或者按下Enter时触发该函数
        editor = self.sender().widget()
        if editor:
            self.CompActivated = True
            editor.close()
            self.CompActivated = False

    def setModelData(self, editor, model, index):
        completer = editor.completer()
        if completer and completer.popup().isVisible() or self.CompActivated:
            current_index = completer.popup().currentIndex()
            if current_index.isValid():
                completion = completer.completionModel().data(current_index)
                last_space_index = completion.rfind(' ')
                if last_space_index != -1:
                    prefix = completion[:last_space_index]
                    model.setData(index, prefix)
                else:
                    model.setData(index, completion)
        else:
            super().setModelData(editor, model, index)


class CustomCompleter(QCompleter):
    def __init__(self, words, maxShowNumber, customListView):
        super().__init__(words)
        # 匹配内容
        self.setFilterMode(Qt.MatchContains)
        # 最大显示行数
        self.setMaxVisibleItems(maxShowNumber)
        # 大小写不敏感
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setPopup(customListView)


class CustomListView(QListView):
    def __init__(self):
        super().__init__()
        self.setUniformItemSizes(True)
        # 视窗采用批量加载模式
        self.setLayoutMode(QListView.Batched)
        # 设置窗体尺寸
        self.setFixedSize(530, 350)
        # 设置其他样式
        self.setStyleSheet("""
            QListView {
                background-color: #272822;
                selection-background-color: #75715E;
                font-size: 22px;
                color: #F8F8F2;
            }
        """)
