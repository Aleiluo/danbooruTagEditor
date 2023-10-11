import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from ui.BatchOperatorWindow import Ui_BatchOperator


def batch_add2begin(tags, text):
    if text not in tags:
        tags.insert(0, text)
    return tags


def batch_add2end(tags, text):
    if text not in tags:
        tags.append(text)
    return tags


def batch_del(tags, text):
    return [tag for tag in tags if tag != text]


def batch_addSlash(tags):
    new_tags = []
    for tag in tags:
        new_tag = ''
        for i in range(len(tag)):
            if tag[i] == '(' and (i == 0 or tag[i - 1] != '\\'):
                new_tag += '\\'
            elif tag[i] == ')' and (i == 0 or tag[i - 1] != '\\'):
                new_tag += '\\'
            new_tag += tag[i]
        new_tags.append(new_tag)
    return new_tags


def batch_delSlash(tags):
    new_tags = []
    for tag in tags:
        new_tag = ''
        tag_len = len(tag)
        for i in range(len(tag)):
            if i < tag_len - 1 and tag[i] == '\\' and (tag[i + 1] == '(' or tag[i + 1] == ')'):
                continue
            else:
                new_tag += tag[i]
        new_tags.append(new_tag)
    return new_tags


def batch_space2underline(tags):
    return [tag.replace(' ', '_') for tag in tags]


def batch_underline2space(tags):
    return [tag.replace('_', ' ') for tag in tags]

class BatchOperator:
    def __init__(self):
        super().__init__()
        # 载入子窗口
        self.batch_operator = QWidget()
        self.batch_operator.ui = Ui_BatchOperator()
        self.batch_operator.ui.setupUi(self.batch_operator)

        # Ctrl+Enter:执行操作
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Enter), self.batch_operator) \
            .activated.connect(self.batch_run)
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Return), self.batch_operator) \
            .activated.connect(self.batch_run)

        # 批处理：批量增加
        self.batch_operator.ui.batchRun.clicked.connect(self.batch_run)
        # 批处理：ComboBox索引更改
        self.batch_operator.ui.comboBox.currentIndexChanged.connect(self.batch_idxChanged)

    def open_BatchOperation(self):
        if self.ui.openBatchOperation.isEnabled():
            # 打开窗口
            self.batch_operator.show()

    def batch_idxChanged(self, index):
        # 设置编辑框的启用状态
        if index == 0:
            # 批量前插
            self.batch_operator.ui.batchEdit.setEnabled(True)
        elif index == 1:
            # 批量后插
            self.batch_operator.ui.batchEdit.setEnabled(True)
        elif index == 2:
            # 批量删除
            self.batch_operator.ui.batchEdit.setEnabled(True)
        elif index == 3:
            # 括号前添加转义符'/'
            self.batch_operator.ui.batchEdit.setEnabled(False)
        elif index == 4:
            # 移除括号前转义符'/'
            self.batch_operator.ui.batchEdit.setEnabled(False)
        elif index == 5:
            # 空格变下划线
            self.batch_operator.ui.batchEdit.setEnabled(False)
        elif index == 6:
            # 下划线变空格
            self.batch_operator.ui.batchEdit.setEnabled(False)

    def batch_run(self):
        # 询问是否保存
        if self.ui.saveConfirm.isChecked():
            if self.SaveConfirm_3opt(title='保存确认', msg='确认保存？') == False:
                return
        else:
            self.saveTags2File()

        # 备份操作
        if self.batch_operator.ui.backup.isChecked():
            self.backupTags()

        batch_mode = self.batch_operator.ui.comboBox.currentIndex()

        # 直接在该函数写循环，而不是在每一个操作函数中写循环
        for image_row in range(self.ui.imageTable.rowCount()):
            # 对过滤后的图片进行批量操作
            if self.ui.imageTable.isRowHidden(image_row):
                continue

            item = self.ui.imageTable.item(image_row, 1)

            if item and item.text() == '':
                continue

            # 重新从文件读取标签
            image_filename = item.text()
            tags_filename = image_filename.replace(".jpg", ".txt").replace(".png", ".txt")
            tags = self.loadTagsfromFile(tags_filename)
            new_tags = []
            if batch_mode == 0:
                # 批量前插
                text = self.batch_operator.ui.batchEdit.text()
                new_tags = batch_add2begin(tags, text)
            elif batch_mode == 1:
                # 批量后插
                text = self.batch_operator.ui.batchEdit.text()
                new_tags = batch_add2end(tags, text)
            elif batch_mode == 2:
                # 批量删除
                text = self.batch_operator.ui.batchEdit.text()
                new_tags = batch_del(tags, text)
            elif batch_mode == 3:
                # 括号前添加转义符'/'
                new_tags = batch_addSlash(tags)
            elif batch_mode == 4:
                # 移除括号前转义符'/'
                new_tags = batch_delSlash(tags)
            elif batch_mode == 5:
                # 空格变下划线
                new_tags = batch_space2underline(tags)
            elif batch_mode == 6:
                # 下划线变空格
                new_tags = batch_underline2space(tags)

            # 将更改后的标签保存到对应的文件
            tags_path = os.path.join(self.folder_path, tags_filename)
            # 保存标签到文件
            with open(tags_path, "w") as file:
                for i, tag in enumerate(new_tags):
                    file.write(tag)
                    if i < len(new_tags) - 1:
                        file.write(", ")

        # 处理完后重载当前标签列表
        self.loadTags2Table()




