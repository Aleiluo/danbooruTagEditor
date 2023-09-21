import os
import re

from time import time

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class fileManager:
    def __init__(self):
        super().__init__()
        self.tagcount = 0
        self.entagChanged = False
        self.curImage_path = ""
        self.curTag_path = ""
        self.folder_path = ""
        # 多线程加载图片
        self.image_loader = imageTableLoader()
        self.image_loader.image_loaded.connect(self.setImageTable)

    # -------------------
    #
    # 保存状态确认
    #
    # -------------------

    def setneedSave(self):
        self.entagChanged = True
        title = self.windowTitle()
        if not title.endswith(" *"):
            self.setWindowTitle(title + " *")

    def sethaveSaved(self):
        self.entagChanged = False
        title = self.windowTitle()
        if title.endswith(" *"):
            self.setWindowTitle(title[:-2])

    # -------------------
    #
    # 消息弹窗
    #
    # -------------------

    def SaveConfirm_2opt(self, title, msg):
        # 2个选项的强制选择窗口
        if self.entagChanged == True:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(title)
            msg_box.setText(msg)
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            # 设置为不可关闭
            msg_box.setWindowFlags(msg_box.windowFlags()
                                   | Qt.CustomizeWindowHint
                                   | Qt.WindowTitleHint)
            msg_box.setWindowFlags(msg_box.windowFlags()
                                   & ~Qt.WindowCloseButtonHint)

            reply = msg_box.exec_()

            if reply == QMessageBox.Yes:
                self.saveTags2File()
                return

            self.sethaveSaved()

    def SaveConfirm_3opt(self, title, msg):
        # 3个选项的非强制选择窗口
        if self.entagChanged:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(title)
            msg_box.setText(msg)
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No
                                       | QMessageBox.Cancel)

            reply = msg_box.exec_()

            if reply == QMessageBox.Yes:
                # 保存并切换
                self.saveTags2File()  # 保存操作
                return True
            elif reply == QMessageBox.No:
                # 切换，但不保存
                self.sethaveSaved()
                return True
            elif reply == QMessageBox.Cancel:
                # 不切换
                return False
        else:
            return True

    # -------------------
    #
    # 变量与文件的读写
    #
    # -------------------

    def setImageTable(self, emit_info):
        for row, pixmap in emit_info:
            pixmap_label = QLabel()
            pixmap_label.setPixmap(pixmap)
            pixmap_label.setAlignment(Qt.AlignCenter)
            self.ui.imageTable.setCellWidget(row, 0, pixmap_label)

    def loadImagesfromFile(self):
        def extract_number_from_filename(filename):
            # 尝试获取图片的序号
            match = re.search(r'\((\d+)\)', filename)
            if match:
                return int(match.group(1))
            return 0

        # 清空操作
        self.ui.imageTable.clearContents()
        self.ui.imageTable.setRowCount(0)
        # 获取文件夹内的图片和标签文件
        image_files = [
            file for file in os.listdir(self.folder_path)
            if file.endswith(".jpg") or file.endswith(".png")
        ]
        # 先按照英文字母排序，再按照括号内的数字大小排序
        image_files_sorted = sorted(image_files,
                                    key=lambda x: (x.split('(')[0],
                                                   extract_number_from_filename(x))
                                    )

        for row, file_name in enumerate(image_files_sorted):
            self.ui.imageTable.insertRow(row)
            file_name_item = QTableWidgetItem(file_name)
            # 设置单元格文本居中对齐
            file_name_item.setTextAlignment(Qt.AlignCenter)
            # 自动换行
            file_name_item.setFlags(file_name_item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.TextWordWrap)
            self.ui.imageTable.setItem(row, 1, file_name_item)

        # 载入对应图像
        self.image_loader.stop()
        self.image_loader.wait()
        self.image_loader.setParams(self.folder_path, image_files_sorted)
        self.image_loader.start()

    # 标签表格
    def loadTagsfromFile(self, tags_file):
        self.curTag_path = os.path.join(self.folder_path, tags_file)
        with open(self.curTag_path, "r") as file:
            tags = file.read().split(",")

        tags = [tag.strip() for tag in tags]
        return tags

    # 标签表格
    def saveTags2File(self):
        tags = self.getTagsfromTable()
        # 保存标签到文件
        with open(self.curTag_path, "w") as file:
            for i, tag in enumerate(tags):
                file.write(tag)
                if i < len(tags) - 1:
                    file.write(", ")
        # 成功保存，标记取消
        self.ui.statusbar.showMessage("标签文件已更新！", 700)
        self.sethaveSaved()

    # -------------------
    #
    # 变量到标签表格
    #
    # -------------------

    def getTagsfromTable(self):
        tags_index = []
        # 保持原始标签顺序输出：按照第三列数字排序输出
        for row in range(self.ui.tagTable.rowCount()):
            # 获取当前行的序号和标签文本
            tag_item = self.ui.tagTable.item(row, 0)
            if tag_item.text() == '' or tag_item.text() == '<NewRow>':
                continue

            tag = tag_item.text()
            index = tag_item.index
            tags_index.append((index, tag))
        if self.ui.oriorder_front.isChecked() or self.ui.oriorder_behind.isChecked():
            # 按照行号排序
            tags_index = sorted(tags_index, key=lambda x: x[0])
        elif self.ui.sortorder.isChecked():
            # 按照字母排序
            tags_index = sorted(tags_index, key=lambda x: x[1])

        return [tag_index[1] for tag_index in tags_index]

    def loadTags2Table(self):
        # 阻塞事件
        self.blockItemchangedConnect = True

        # 清空表格
        self.ui.tagTable.clearContents()
        self.ui.tagTable.setRowCount(0)
        # 获取当前图片对应的标签文件
        tags_file = self.curImage.replace(".jpg",
                                          ".txt").replace(".png", ".txt")
        tags = self.loadTagsfromFile(tags_file)

        # 添加标签
        self.tagcount = 0
        for i, en_tag in enumerate(tags):
            # 去空格
            en_tag = en_tag.strip()
            # 添加新行到表格
            self.ui.tagTable.insertRow(i)
            # 添加英文标签到第一列
            en_tag_item = QTableWidgetItem(en_tag)
            self.tagcount += 1
            en_tag_item.index = self.tagcount
            self.ui.tagTable.setItem(i, 0, en_tag_item)
            # 添加翻译标签到第二列
            translated_tag_item = QTableWidgetItem(self.translateTag(en_tag))
            self.ui.tagTable.setItem(i, 1, translated_tag_item)

        # 排序
        self.ui.tagTable.sortItems(0, Qt.AscendingOrder)

        # 恢复事件
        self.blockItemchangedConnect = False

    # -------------------
    #
    # 其他函数
    #
    # -------------------

    def selectFolder(self):
        # 先关闭所有窗口
        self.workingflow_window.close()
        self.filter_window.close()

        # 选择文件夹一定会弹窗询问
        if self.SaveConfirm_3opt(title='保存确认', msg='确认保存？') == False:
            return

        # 打开文件夹选择对话框
        folder_dialog = QFileDialog()
        folder_dialog.setFileMode(QFileDialog.Directory)
        folder_dialog.setOption(QFileDialog.ShowDirsOnly, True)

        if folder_dialog.exec_():
            self.folder_path = folder_dialog.selectedFiles()[0]
            # 加载图片
            self.loadImagesfromFile()
            # 关闭预览图
            if self.imageShowed == True:
                self.switch_image_preview()

            # 保存功能
            self.ui.saveFile.setEnabled(True)
            # 过滤器
            self.filter_loadFile()
            self.ui.openFilter.setEnabled(True)
            self.ui.clearFilter.setEnabled(True)
            # 应用过滤器
            self.filter_apply(filterimage=True)
            # 工作流
            self.wf_loadFile()
            self.ui.openWorkingFlow.setEnabled(True)


class imageTableLoader(QThread):
    image_loaded = pyqtSignal(list)
    stop_thread = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.batchSize = 30
        self.folder_path = ''
        self.file_names = []
        self.stop_flag = False

    def setParams(self, folder_path, file_names):
        self.folder_path = folder_path
        self.file_names = file_names
        self.stop_flag = False

    def stop(self):
        self.stop_flag = True

    def run(self):
        emit_image_info = []
        t1 = time()
        # 图片加载
        for i, file_name in enumerate(self.file_names):
            if self.stop_flag:
                return

            image_path = os.path.join(self.folder_path, file_name)
            # 读取并缩放图像
            image_reader = QImageReader(image_path)
            image_reader.setAutoTransform(True)
            image = image_reader.read()
            image = image.scaled(160, 160, Qt.KeepAspectRatio)
            emit_image_info.append((i, QPixmap.fromImage(image)))

            if (i + 1) % self.batchSize == 0:
                t2 = time()
                print(t2 - t1)
                t1 = time()
                self.image_loaded.emit(emit_image_info)
                emit_image_info = []

        # 最后也要返回一次
        self.image_loaded.emit(emit_image_info)

