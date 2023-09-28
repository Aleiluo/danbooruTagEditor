import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


def textRepeatRows(self, text):
    # 获取匹配的行列表
    repeat_rows = []
    for row in range(self.ui.tagTable.rowCount()):
        cur_item = self.ui.tagTable.item(row, 0)
        if cur_item is not None and cur_item.text() == text:
            repeat_rows.append(row)

    return repeat_rows


def refreshTagtable(self, item, old_text=''):
    # 该函数不设撤销重做操作
    item_column = item.column()
    item_row = item.row()
    item_text = item.text().strip()

    if item_column == 0:
        repeat_rows = textRepeatRows(self, item_text)
        if len(repeat_rows) > 1:
            # 强行聚焦避免出现无法删除的情况
            self.ui.tagTable.setFocus()
            # 没有撤销重做，所以改回旧文本再删，这样Del的撤销就有效了
            item.setText(old_text)
            self.delTagtableRow([item])
            return False
        else:
            # 翻译
            translated_text = self.translateTag(item_text)
            translated_item = QTableWidgetItem(translated_text)
            self.ui.tagTable.setItem(item_row, 1, translated_item)
            # 排序
            self.ui.tagTable.sortItems(0, Qt.AscendingOrder)
            # 排序后移动视野到item_text的位置

            found_items = self.ui.tagTable.findItems(item_text,
                                                     Qt.MatchExactly)
            if len(found_items) > 0:
                found_item = found_items[0]
                found_item_row = found_item.row()
                self.ui.tagTable.setCurrentCell(found_item_row, 0)
                self.ui.tagTable.scrollToItem(self.ui.tagTable.item(found_item_row, 0))
            return True

    elif item_column == 1:
        # 第二列内容更改
        # 获取该行第一列的内容
        en_item = self.ui.tagTable.item(item_row, 0)
        cn_item = self.ui.tagTable.item(item_row, 1)
        if en_item is not None and cn_item is not None:
            en_text = en_item.text().strip()
            cn_text = cn_item.text().strip()
            # 更新字典
            self.update_translation(en_text, cn_text)
            # 将翻译结果保存
            self.write_translation_file()
            return True
        else:
            return False


class UserEvents:
    def __init__(self):
        super().__init__()
        # 加载剪贴板
        self.clipboard = QApplication.clipboard()
        # 当前选中图片
        self.curImage = None
        # 预览图是否正在显示
        self.imageShowed = False
        # 是否阻断物件修改触发事件
        self.blockItemchangedConnect = False
        # 图片显示相关
        self.left_region = QRegion(0, 0, self.width() * 3 / 7, self.height())
        self.mouseinLeftRegion = False
        # 单击时记录tag信息方便撤销操作
        self.cur_items = None
        self.cur_item = None
        self.cur_text = None
        # 记录鼠标是否离开窗口
        self.main_left = False
        self.wf_left = False

        # -------------------
        #
        # 热键与事件Shortcuts & Events
        #
        # -------------------

        # Shift + V：将剪切板内容添加到标签列表
        QShortcut(QKeySequence(Qt.ShiftModifier + Qt.Key_V), self) \
            .activated.connect(lambda: self.addRow(self.clipboard.text().strip()))
        # Ctrl + Z：撤销
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Z), self) \
            .activated.connect(self.tagtableUndo)
        # Ctrl + Y：重做
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Y), self) \
            .activated.connect(self.tagtableRedo)
        # Ctrl + N：添加一个新的空行
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_N), self) \
            .activated.connect(self.addRow)
        # Ctrl + V：将剪切板内容覆盖选中内容
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_V), self) \
            .activated.connect(
            lambda: self.overrideText(self.cur_item, self.clipboard.text().strip(), self.cur_text))
        # Ctrl + S：保存
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_S), self) \
            .activated.connect(self.saveTags2File)
        # Ctrl + F：打开过滤器
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_F), self) \
            .activated.connect(self.open_Filter)
        # Ctrl + W：打开工作流
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_W), self) \
            .activated.connect(self.open_WorkingFlow)
        # Alt + S：打开预览图
        QShortcut(QKeySequence(Qt.AltModifier + Qt.Key_S), self) \
            .activated.connect(self.switch_image_preview)
        # Alt + Up：选择上一张图片
        QShortcut(QKeySequence(Qt.AltModifier + Qt.Key_Up), self) \
            .activated.connect(self.prevImage)
        # Alt + Down：选择下一张图片
        QShortcut(QKeySequence(Qt.AltModifier + Qt.Key_Down), self) \
            .activated.connect(self.nextImage)
        # Del
        QShortcut(QKeySequence(Qt.Key_Delete), self) \
            .activated.connect(lambda: self.delTagtableRow(self.cur_items))

        # 连接图片列表的选择事件
        self.ui.imageTable.itemSelectionChanged.connect(self.selectImage)
        # 标签列表：物件更改事件--带阻拦的编辑模式
        self.ui.tagTable.itemChanged.connect(self.editmode)
        # 标签列表：激活物件事件--获取当前物件文本
        self.ui.tagTable.itemSelectionChanged.connect(self.delayed_getCurtext)

    def tagtableUndo(self):
        self.undoStack.undo()
        self.wf_FontReset()

    def tagtableRedo(self):
        self.undoStack.redo()
        self.wf_FontReset()

    def eventFilter(self, source, event):
        # 全局事件过滤器
        if event.type() == QEvent.Wheel:
            # Alt
            if event.modifiers() & Qt.AltModifier:
                # Alt + 滚轮
                # 该事件触发时，锁定所有滑动条提升用户体验
                for scrollArea in self.findChildren(QScrollBar):
                    scrollArea.setEnabled(False)
                if event.angleDelta().x() != 0:
                    delta = event.angleDelta().x()
                else:
                    delta = event.angleDelta().y()
                if delta > 0:
                    self.prevImage()
                    return True
                elif delta < 0:
                    self.nextImage()
                    return True
        elif event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                if source == self:
                    if self.ui.imageTable.hasFocus():
                        # 如果焦点在imageTable
                        self.ui.tagTable.setFocus()
                    elif self.ui.tagTable.hasFocus():
                        self.ui.tagTable.editItem(self.ui.tagTable.currentItem())

                elif source == self.workingflow_window:
                    self.wf_EnterPressed()

            elif event.key() == Qt.Key_Escape and self.ui.tagTable.hasFocus():
                if source == self:
                    self.ui.imageTable.setFocus()

        elif event.type() == QEvent.ContextMenu:
            # 在mainWindow中右键对应的事件是QEvent.ContextMenu
            if source == self.workingflow_window:
                en_item = self.wf_curEnItem()
                if en_item:
                    del_text = en_item.text().strip()
                    row = textRepeatRows(self, del_text)
                    if len(row) > 0:
                        self.delTagtableRow([self.ui.tagTable.item(row[0], 0)])

        elif event.type() == QMouseEvent.HoverMove and source == self:
            # 判断鼠标是否在左侧区域内
            if self.imageShowed == True:
                if self.left_region.contains(event.pos()) == True:
                    self.mouseinLeftRegion = True
                    # 鼠标进入图片区域时将透明度过渡到0.3
                    self.opacity_animation.setEndValue(0.3)
                    self.opacity_animation.start()
                    # 开启穿透
                    self.preview_image.setAttribute(
                        Qt.WA_TransparentForMouseEvents, True)
                    return True
                else:
                    self.mouseinLeftRegion = False
                    # 鼠标离开图片区域时将透明度过渡到1.0（不透明）
                    self.opacity_animation.setEndValue(1.0)
                    self.opacity_animation.start()
                    # 结束穿透
                    self.preview_image.setAttribute(
                        Qt.WA_TransparentForMouseEvents, False)
                    return True
        elif event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Alt:
                for scrollArea in self.findChildren(QScrollBar):
                    scrollArea.setEnabled(True)

        return False

    def resizeEvent(self, event):
        # 窗口大小改变时更新左侧区域
        self.left_region = QRegion(0, 0, self.width() * 3 / 7, self.height())
        if self.imageShowed == True:
            self.switch_image_preview()
            QTimer.singleShot(300, self.switch_image_preview)

    def closeEvent(self, event):
        if self.entagChanged == True:
            reply = QMessageBox.question(
                self, "保存确认", "Save?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.saveTags2File()  # 保存操作
                self.close()  # 关闭窗口
                self.filter_window.close()
                self.workingflow_window.close()
            elif reply == QMessageBox.No:
                self.close()  # 关闭窗口
                self.filter_window.close()
            elif reply == QMessageBox.Cancel:
                pass  # 取消关闭窗口
        else:
            self.close()
            self.filter_window.close()
            self.workingflow_window.close()

    # -------------------
    #
    # 图片表格imageTable
    #
    # -------------------

    def selectImage(self):
        def select_first_visible_row(table: QTableWidget):
            for row in range(table.rowCount()):
                if not table.isRowHidden(row):
                    table.setCurrentCell(row, 0)
                    break

        # 确定保存
        if self.ui.saveConfirm.isChecked():
            if self.SaveConfirm_3opt(title='保存确认', msg='确认保存？') == False:
                return
        else:
            self.saveTags2File()

        selected_items = self.ui.imageTable.selectedItems()
        if len(selected_items) > 0:
            self.imageTableRow = selected_items[0].row()
            text_item = self.ui.imageTable.item(self.imageTableRow, 1)
            self.curImage = text_item.text()
            self.loadTags2Table()
            # 如果预览图正在显示，那么切换预览图为当前图片
            if self.imageShowed == True:
                self.switch_image_preview()
                self.switch_image_preview()
            # 清空撤销栈
            self.undoStack.clear()
            # 应用过滤器到主窗口(选择图片不进行图片过滤操作)
            self.filter_apply(filterimage=False)
            # 选择第一个没有隐藏的内容
            if self.ui.tagTable.rowCount() > 0:
                select_first_visible_row(self.ui.tagTable)


    def prevImage(self):
        total_rows = self.ui.imageTable.rowCount()
        if total_rows == 0:
            return

        new_row = self.imageTableRow
        # 向前遍历图片列表，找到下一个未隐藏的图片项
        while True:
            new_row = (new_row - 1) % total_rows
            if not self.ui.imageTable.isRowHidden(new_row):
                break

        # 设置当前选择为新的行
        self.ui.imageTable.setCurrentCell(new_row, 0)

    def nextImage(self):
        total_rows = self.ui.imageTable.rowCount()
        if total_rows == 0:
            return

        new_row = self.imageTableRow
        while True:
            new_row = (new_row + 1) % total_rows
            if not self.ui.imageTable.isRowHidden(new_row):
                break
        self.ui.imageTable.setCurrentCell(new_row, 0)

    def switch_image_preview(self):

        # 切换图片显示或者隐藏
        if self.imageShowed == False:
            # 如果图片隐藏
            if self.curImage:
                image_path = os.path.join(self.folder_path, self.curImage)
                pixmap = QPixmap(image_path)

                self.preview_image = QLabel(self)
                self.preview_image.resize(self.width() * 3 / 7, self.height())

                # 设置标签背景颜色为透明色
                self.preview_image.setStyleSheet(
                    "background-color: transparent;")

                # 自适应缩放图像并去除黑边
                self.preview_image.setPixmap(
                    pixmap.scaled(self.preview_image.size(),
                                  Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.SmoothTransformation))

                # 将预览标签的位置设置在屏幕的左侧
                self.preview_image.move(0, 0)
                self.preview_image.setWindowFlags(Qt.WindowStaysOnTopHint)

                # 添加透明效果
                self.opacity_effect = QGraphicsOpacityEffect()
                if self.mouseinLeftRegion == True:
                    # 如果鼠标在屏幕左侧三分之一处，图像初始是透明的
                    self.opacity_effect.setOpacity(0.3)
                else:
                    self.opacity_effect.setOpacity(1)

                self.preview_image.setGraphicsEffect(self.opacity_effect)

                # 创建动画对象来实现透明度的过渡效果
                self.opacity_animation = QPropertyAnimation(
                    self.opacity_effect, b"opacity")
                self.opacity_animation.setDuration(250)

                self.preview_image.show()

            self.imageShowed = True
        else:
            if self.preview_image is not None:
                self.preview_image.close()
                self.preview_image = None

            self.imageShowed = False

    # -------------------
    #
    # 标签列表tagTable
    #
    # -------------------

    def delayed_getCurtext(self):
        # 设置50毫秒的延迟避免频繁读取
        QTimer.singleShot(50, self.getCurtext)

    def getCurtext(self):
        self.cur_items = self.ui.tagTable.selectedItems()
        if len(self.cur_items) > 0:
            self.cur_item = self.cur_items[0]
            self.cur_text = self.cur_item.text().strip()
            try:
                print(self.cur_item.index)
            except:
                pass

    def editmode(self):
        # 技术有限，用间接方法来处理编辑模式
        if self.blockItemchangedConnect == True:
            return

        old_text = self.cur_text
        new_text = self.cur_item.text().strip()
        # 编辑模式相当于覆写操作
        self.overrideText(self.cur_item, new_text, old_text)

    def overrideText(self, item, new_text, old_text):
        # 阻塞事件
        self.blockItemchangedConnect = True

        # 修改文本
        item.setText(new_text)
        # 添加到快捷拷贝列表(更改英文标签才添加，更改翻译不添加)
        if item.column() == 0:
            if refreshTagtable(self, item, old_text) == True:
                # 设置为需要保存
                self.setneedSave()
                # 添加撤销重做命令
                command = OverrideTextCommand(self, item, new_text, old_text)
                # 添加撤销命令到撤销栈
                self.undoStack.push(command)
        elif item.column() == 1:
            # 如果更改翻译只进行更新操作即可
            refreshTagtable(self, item)

        # 恢复事件
        self.blockItemchangedConnect = False

    def addRow(self, text='<NewRow>'):
        def getTagCount(self):
            if self.ui.oriorder_front.isChecked():
                # 前插模式
                return self.front_const
            elif self.ui.oriorder_behind.isChecked():
                # 后插模式
                return self.behind_const
            elif self.ui.sortorder.isChecked():
                # 排序模式与标签无关
                return self.sort_count

        # 先验证有没有重复，再添加
        repeat_rows = textRepeatRows(self, text)
        if len(repeat_rows) == 0:
            self.blockItemchangedConnect = True
            if text != '<NewRow>':
                row = 0
            else:
                row = self.cur_item.row()

            # 添加一行
            self.ui.tagTable.clearSelection()  # 取消所有选中
            self.ui.tagTable.insertRow(row)
            # 插入的一行有文本
            item = QTableWidgetItem(text)
            item.index = getTagCount(self)
            self.ui.tagTable.setItem(row, 0, item)
            self.ui.tagTable.setCurrentCell(row, 0)

            if text != '<NewRow>':
                # 添加新行不要立刻排序
                refreshTagtable(self, item)

            # 设置为需要保存
            self.setneedSave()
            # 创建撤销命令
            command = AddRowCommand(self, item.index, text)
            # 添加撤销命令到撤销栈
            self.undoStack.push(command)

            self.blockItemchangedConnect = False
        else:
            self.ui.tagTable.setCurrentCell(repeat_rows[0], 0)

    def delTagtableRow(self, items):
        # 阻塞事件
        self.blockItemchangedConnect = True
        # 获取行索引列表
        selected_rows = set()
        for item in items:
            selected_rows.add(item.row())
        # 删除操作的行要逆序排序
        selected_rows = sorted(selected_rows, reverse=True)

        rowsInfo = []
        for row in selected_rows:
            rowsInfo.append([
                self.ui.tagTable.item(row, 0).index,
                self.ui.tagTable.item(row, 0).text()
            ])
        # 反着删除
        for row in selected_rows:
            self.ui.tagTable.removeRow(row)
        # 设置为需要保存
        self.setneedSave()
        # 创建撤销命令
        command = DeleteRowsCommand(self, rowsInfo)
        # 添加撤销命令到撤销栈
        self.undoStack.push(command)

        # 恢复事件
        self.blockItemchangedConnect = False

        # 删除后更新工作表
        self.wf_FontReset()

    def changeTagTableIndex(self, sort_mode):
        def change_index(self, new_index):
            for row in range(self.ui.tagTable.rowCount()):
                item = self.ui.tagTable.item(row, 0)
                idx = item.index
                if (idx == self.front_const or
                        idx == self.behind_const or
                        idx == self.sort_const):
                    item.index = new_index

        # 遍历表格，更改item的index
        if sort_mode == 0:
            # 前插
            change_index(self, self.front_const)
        elif sort_mode == 1:
            # 后插
            change_index(self, self.behind_const)
        elif sort_mode == 2:
            # 排序
            change_index(self, self.sort_const)

# -----------------
#
# 撤销命令类
#
# -----------------


class OverrideTextCommand(QUndoCommand):
    def __init__(self, main_self, item, new_text, old_text):
        super().__init__()
        self.main = main_self
        self.item = item
        self.new_text = new_text
        self.old_text = old_text

    def redo(self):
        self.main.blockItemchangedConnect = True
        self.item.setText(self.new_text)
        refreshTagtable(self.main, self.item)
        self.main.blockItemchangedConnect = False

    def undo(self):
        self.main.blockItemchangedConnect = True
        self.item.setText(self.old_text)
        refreshTagtable(self.main, self.item)
        self.main.blockItemchangedConnect = False


class AddRowCommand(QUndoCommand):
    # 新增一个空行
    def __init__(self, main_self, ind, text):
        super().__init__()
        self.main = main_self
        self.ind = ind
        self.text = text

    def redo(self):
        # 添加行
        self.main.blockItemchangedConnect = True
        self.main.ui.tagTable.insertRow(0)
        item = QTableWidgetItem(self.text)
        item.index = self.ind
        self.main.ui.tagTable.setItem(0, 0, item)

        refreshTagtable(self.main, item)
        self.main.blockItemchangedConnect = False

    def undo(self):
        # 删除行
        self.main.blockItemchangedConnect = True
        found_items = self.main.ui.tagTable.findItems(self.text,
                                                      Qt.MatchExactly)
        if len(found_items) > 0:
            found_item = found_items[0]
            self.main.ui.tagTable.removeRow(found_item.row())
        self.main.blockItemchangedConnect = False


class DeleteRowsCommand(QUndoCommand):
    def __init__(self, main_self, RowInfo):
        # Del不参与更新函数，所以传进来删除的行和物件
        super().__init__()
        self.main = main_self
        self.RowInfo = RowInfo

    def redo(self):
        self.main.blockItemchangedConnect = True
        # 为了避免莫名奇妙的bug，查找进行删除
        for info in self.RowInfo:
            found_items = self.main.ui.tagTable.findItems(
                info[1], Qt.MatchExactly)
            if len(found_items) > 0:
                found_item = found_items[0]
                self.main.ui.tagTable.removeRow(found_item.row())

        self.main.blockItemchangedConnect = False

    def undo(self):
        self.main.blockItemchangedConnect = True
        # 直接在末尾添加一个，刷新一次，时间复杂度拉满
        for info in self.RowInfo:
            self.main.ui.tagTable.insertRow(0)
            item = QTableWidgetItem(info[1])
            item.index = info[0]
            self.main.ui.tagTable.setItem(0, 0, item)

            refreshTagtable(self.main, item)

        self.main.blockItemchangedConnect = False
