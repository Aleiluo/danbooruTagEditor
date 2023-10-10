import json
import os
import re
import shutil

from datetime import datetime

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class FileManager:
    image_loaded = pyqtSignal(int, QPixmap)

    def __init__(self):
        super().__init__()
        # 已经处理的图片数
        self.full_working_state = {}
        self.imageTableRow = 0
        self.tagcount = 0
        self.entagChanged = False
        self.curImage_path = ""
        self.curTag_path = ""
        self.folder_path = ""
        # 多线程加载图片
        self.thread_pool = QThreadPool()
        # 开多了加载时会卡顿
        self.thread_pool.setMaxThreadCount(10)
        self.image_loaded.connect(self.setImageTable)

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

    def loadWorkingState(self):
        # 读取文件中的工作流
        try:
            with open('./cache/WorkingState.txt', 'r') as f:
                self.full_working_state = json.load(f)

            working_state = self.full_working_state[self.folder_path]
            self.imageTableRow = working_state['imageTableRow']
        except:
            pass

    def saveWorkingState(self):
        # 将工作流信息写入到信息字典
        self.full_working_state[self.folder_path] = {
            'imageTableRow': self.imageTableRow,
        }
        # 保存到文件
        if not os.path.exists('./cache'):
            os.makedirs('./cache')
        with open('./cache/WorkingState.txt', 'w') as f:
            json.dump(self.full_working_state, f)

    def setImageTable(self, row, pixmap):
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

        # 载入图像
        for row, file_name in enumerate(image_files_sorted):
            self.ui.imageTable.insertRow(row)
            file_name_item = QTableWidgetItem(file_name)
            # 文字居中
            file_name_item.setTextAlignment(Qt.AlignCenter)
            # 自动换行
            file_name_item.setFlags(file_name_item.flags() |
                                    Qt.ItemIsSelectable |
                                    Qt.ItemIsEnabled |
                                    Qt.TextWordWrap)
            self.ui.imageTable.setItem(row, 1, file_name_item)
            # 创建并运行工作线程
            image_path = os.path.join(self.folder_path, file_name)
            worker = ImageLoaderThread(row, image_path, self.image_loaded)
            self.thread_pool.start(worker)

    # 标签表格
    def loadTagsfromFile(self, tags_file):
        self.curTag_path = os.path.join(self.folder_path, tags_file)
        with open(self.curTag_path, "r") as file:
            tags = file.read().split(",")

        tags = [tag.strip() for tag in tags]
        return tags

    # 标签表格
    def saveTags2File(self):
        # 保存工作状态
        self.saveWorkingState()
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
    # 选择文件夹
    #
    # -------------------

    def selectFolder(self):
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
            # 清空标签列表
            self.ui.tagTable.clearContents()
            self.ui.tagTable.setRowCount(0)
            # 关闭预览图
            if self.imageShowed == True:
                self.switch_image_preview()

            # 保存功能
            self.ui.saveFile.setEnabled(True)
            # 读取工作状态
            self.loadWorkingState()
            self.ui.imageTable.setCurrentCell(self.imageTableRow, 1)
            self.ui.imageTable.scrollToItem(self.ui.imageTable.item(self.imageTableRow, 1))
            # 过滤器
            self.filter_loadFile()
            self.ui.openFilter.setEnabled(True)
            self.ui.clearFilter.setEnabled(True)
            # 应用过滤器
            self.filter_apply(filterimage=True)
            # 工作流
            self.wf_loadFile()
            self.ui.openWorkingFlow.setEnabled(True)
            # 批量处理
            self.ui.openBatchOperation.setEnabled(True)

    # -------------------
    #
    # 备份标签
    #
    # -------------------

    def backupTags(self):
        # 对于批处理操作写撤销重做比较麻烦，索性直接备份所有标签文件

        # 获取最后一级文件目录
        base_name = os.path.basename(os.path.normpath(self.folder_path))
        # 获取时间
        current_time = datetime.now().strftime("%m-%d-%H-%M-%S")
        # 生成备份路径
        backup_path = os.path.join('./backup', base_name, current_time)
        os.makedirs(backup_path, exist_ok=True)

        # 拷贝标签文件到备份路径
        for file_name in os.listdir(self.folder_path):
            if file_name.endswith('.txt') and os.path.isfile(os.path.join(self.folder_path, file_name)):
                shutil.copy(os.path.join(self.folder_path, file_name), backup_path)

        self.ui.statusbar.showMessage(f"标签文件备份到{backup_path}", 2000)


class ImageLoaderThread(QRunnable):
    def __init__(self, row, image_path, return_signal):
        super().__init__()
        self.row = row
        self.image_path = image_path
        self.return_signal = return_signal

    def run(self):
        image_reader = QImageReader(self.image_path)
        image_reader.setAutoTransform(True)
        image = image_reader.read().scaled(160, 160, Qt.KeepAspectRatio)
        pixmap = QPixmap.fromImage(image)
        self.return_signal.emit(self.row, pixmap)

