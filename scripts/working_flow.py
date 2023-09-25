import json
import os
import win32gui
import win32con

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from ui.WorkingFlowWindow import Ui_WorkingFlow


class workingFlow:
    def __init__(self):
        super().__init__()
        # 载入子窗口
        self.workingflow_window = QWidget()
        self.workingflow_window.ui = Ui_WorkingFlow()
        self.workingflow_window.ui.setupUi(self.workingflow_window)
        # 添加热键
        # Ctrl + N：添加行
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_N), self.workingflow_window) \
            .activated.connect(self.wf_addRow)
        # Del：删除行
        QShortcut(QKeySequence(Qt.Key_Delete), self.workingflow_window) \
            .activated.connect(self.wf_deleteRow)
        # Left：上一页
        QShortcut(QKeySequence(Qt.Key_Left), self.workingflow_window) \
            .activated.connect(lambda: self.wf_SwitchPage(self.wf_cur_page - 1))
        # Right：下一页
        QShortcut(QKeySequence(Qt.Key_Right), self.workingflow_window) \
            .activated.connect(lambda: self.wf_SwitchPage(self.wf_cur_page + 1))

        # 与主窗口相连接的快捷键

        # Ctrl + S：保存
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_S), self.workingflow_window) \
            .activated.connect(self.saveTags2File)
        # Ctrl + Z：撤销
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Z), self.workingflow_window) \
            .activated.connect(self.tagtableUndo)
        # Ctrl + Y：重做
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Y), self.workingflow_window) \
            .activated.connect(self.tagtableRedo)
        # Alt + S：打开预览图
        QShortcut(QKeySequence(Qt.AltModifier + Qt.Key_S), self.workingflow_window) \
            .activated.connect(self.switch_image_preview)
        # Alt + Up：选择上一张图片
        QShortcut(QKeySequence(Qt.AltModifier + Qt.Key_Up), self.workingflow_window) \
            .activated.connect(self.prevImage)
        # Alt + Down：选择下一张图片
        QShortcut(QKeySequence(Qt.AltModifier + Qt.Key_Down), self.workingflow_window) \
            .activated.connect(self.nextImage)

        # 工作流：复制内容
        self.workingflow_window.ui.wf_table.cellPressed.connect(self.wf_copy2tagTable)
        # 工作流：上一页
        self.workingflow_window.ui.wf_prepage.clicked.connect(
            lambda: self.wf_SwitchPage(self.wf_cur_page - 1))
        # 工作流：下一页
        self.workingflow_window.ui.wf_nextpage.clicked.connect(
            lambda: self.wf_SwitchPage(self.wf_cur_page + 1))
        # 工作流：首页
        self.workingflow_window.ui.wf_homepage.clicked.connect(
            lambda: self.wf_SwitchPage(0))
        # 工作流：尾页
        self.workingflow_window.ui.wf_lastpage.clicked.connect(
            lambda: self.wf_SwitchPage(len(self.wf_spaceinfo) - 1))
        # 工作流：插入页
        self.workingflow_window.ui.wf_insertpage.clicked.connect(
            lambda: self.wf_insertNewPage(self.wf_cur_page + 1))
        # 工作流：删除当前页
        self.workingflow_window.ui.wf_delpage.clicked.connect(
            lambda: self.wf_delCurrentPage(self.wf_cur_page))
        # 工作流：工作模式切换
        self.workingflow_window.ui.buttonGroup.buttonToggled.connect(self.wf_workingModeChanged)
        # 更改工作流表格信息
        self.workingflow_window.ui.wf_table.itemChanged.connect(self.wf_overrideText)
        # 选择变更
        # self.workingflow_window.ui.wf_table.itemSelectionChanged.connect(self.wf_clearSelection)

        # 信息记录变量
        # 所有工作区域的工作流
        self.wf_fullinfo = {}
        # 当前工作区域的工作流
        self.wf_spaceinfo = []
        # 当前工作区域的工作流的每页的分组名称
        self.wf_spacename = []
        # 当前工作模式，默认编辑模式
        self.wf_workingMode = 'editing'
        # 当前页码
        self.wf_cur_page = 0
        # 阻挡更新函数
        self.wf_blockConnect = False
        self.wf_blockAddRow = False
        self.wf_blockDeleteRow = False

    # -------------------
    #
    # 窗口操作
    #
    # -------------------

    def open_WorkingFlow(self):
        if self.ui.openWorkingFlow.isEnabled():
            # 打开窗口
            self.workingflow_window.show()
            # 每次开启跳转到第一页
            self.wf_SwitchPage(0)
            # 切换换到离开时的工作模式
            if self.wf_workingMode == 'editing':
                self.workingflow_window.ui.wf_editmode.setChecked(True)
            elif self.wf_workingMode == 'working':
                self.workingflow_window.ui.wf_workmode.setChecked(True)
            # 实时染色
            self.ui.tagTable.itemChanged.connect(self.wf_FontReset)

    # -------------------
    #
    # 数据在文件与变量之间的存取
    #
    # -------------------

    def wf_loadFile(self):
        # 读取文件中的工作流
        try:
            with open('./cache/WorkingFlowInfo.txt', 'r') as f:
                self.wf_fullinfo = json.load(f)

            cur_fullInfo = self.wf_fullinfo[self.folder_path]
            self.wf_workingMode = cur_fullInfo['workingmode']
            self.wf_spaceinfo = cur_fullInfo['spaceinfo']
            self.wf_spacename = cur_fullInfo['spacename']
        except:
            pass

    def wf_saveFile(self):
        # 将工作流信息写入到信息字典
        self.wf_fullinfo[self.folder_path] = {
            'workingmode': self.wf_workingMode,
            'spaceinfo': self.wf_spaceinfo,
            'spacename': self.wf_spacename
        }
        # 保存到文件
        if not os.path.exists('./cache'):
            os.makedirs('./cache')
        with open('./cache/WorkingFlowInfo.txt', 'w') as f:
            json.dump(self.wf_fullinfo, f)

    # -------------------
    #
    # 数据在表格与变量之间的存取
    #
    # -------------------

    def wf_getTagAndTitle(self):
        # 保存tag与分组名
        self.wf_spaceinfo[self.wf_cur_page] = self.wf_getTag()
        label_text = self.workingflow_window.ui.wf_insEdit.text()
        if label_text == '<分组名称>':
            self.wf_spacename[self.wf_cur_page] = ''
        else:
            self.wf_spacename[self.wf_cur_page] = label_text

    def wf_loadTagAndTitle(self, page):
        # 载入tag与分组名
        if page > len(self.wf_spaceinfo) - 1:
            return

        self.wf_loadTag(page=page)
        label_text = self.wf_spacename[page]
        if label_text == '':
            self.workingflow_window.ui.wf_insEdit.setText('<分组名称>')
        else:
            self.workingflow_window.ui.wf_insEdit.setText(label_text)

    def wf_getTag(self):
        # 读取表格中的内容
        tag_list = []
        for row in range(self.workingflow_window.ui.wf_table.rowCount()):
            item = self.workingflow_window.ui.wf_table.item(row, 0)
            item_text = item.text().strip()
            if item_text != '':
                tag_list.append(item_text)
        return tag_list

    def wf_loadTag(self, page):
        self.wf_blockConnect = True
        # 写入对应页的工作流标签，并且标注出标签列表已有的标签
        tag_list = self.wf_spaceinfo[page]
        rowPosition = self.workingflow_window.ui.wf_table.rowCount()
        for tag in tag_list:
            # 中英item
            en_item = QTableWidgetItem(tag)
            translated_text = self.translateTag(tag)
            cn_item = QTableWidgetItem(translated_text)
            # 将item插入新的一行
            self.workingflow_window.ui.wf_table.insertRow(rowPosition)
            self.workingflow_window.ui.wf_table.setItem(rowPosition, 0, en_item)
            self.workingflow_window.ui.wf_table.setItem(rowPosition, 1, cn_item)
            rowPosition += 1
        self.wf_blockConnect = False

    def wf_FontReset(self):
        if not self.workingflow_window.isVisible():
            return

        if self.workingflow_window.ui.wf_workmode.isChecked():
            # 工作模式：对重复的item渲染上预设颜色
            tagTable_exist = {}
            # 扫描一遍标签列表
            for row in range(self.ui.tagTable.rowCount()):
                cur_item = self.ui.tagTable.item(row, 0)
                if cur_item is not None:
                    tagTable_exist[cur_item.text().strip()] = 1
            # 再扫描一遍工作流列表上色
            for row in range(self.workingflow_window.ui.wf_table.rowCount()):
                cur_item1 = self.workingflow_window.ui.wf_table.item(row, 0)
                cur_item2 = self.workingflow_window.ui.wf_table.item(row, 1)
                try:
                    font = cur_item1.font()
                    if tagTable_exist.get(cur_item1.text().strip(), -1) == 1:
                        # 使用删除线与斜体
                        font.setStrikeOut(True)
                        font.setItalic(True)
                    else:
                        font.setStrikeOut(False)
                        font.setItalic(False)

                    cur_item1.setFont(font)
                    cur_item2.setFont(font)
                except:
                    pass
        else:
            # 编辑模式：不使用删除线
            for row in range(self.workingflow_window.ui.wf_table.rowCount()):
                cur_item1 = self.workingflow_window.ui.wf_table.item(row, 0)
                cur_item2 = self.workingflow_window.ui.wf_table.item(row, 1)
                try:
                    font = cur_item1.font()
                    font.setStrikeOut(False)
                    font.setItalic(False)
                    cur_item1.setFont(font)
                    cur_item2.setFont(font)
                except:
                    pass

    # -------------------
    #
    # 用户操作
    #
    # -------------------

    def wf_addRow(self):
        if self.wf_blockAddRow == True:
            return

        self.wf_blockConnect = True
        # 获取当前选择，并插入到选择的后一个
        cur_items = self.workingflow_window.ui.wf_table.selectedItems()
        self.workingflow_window.ui.wf_table.clearSelection()
        if len(cur_items) == 1:
            # 如果只选择了一个，就在后面新建一行
            item = cur_items[0]
            row = item.row() + 1
        else:
            # 否则在尾部新建一行
            row = self.workingflow_window.ui.wf_table.rowCount()

        self.workingflow_window.ui.wf_table.insertRow(row)
        self.workingflow_window.ui.wf_table.setItem(row, 0, QTableWidgetItem(''))
        self.workingflow_window.ui.wf_table.setCurrentCell(row, 0)

        self.wf_blockConnect = False

    def wf_deleteRow(self):
        if self.wf_blockDeleteRow == True:
            return

        self.wf_blockConnect = True
        # 删除选中的行
        select_items = self.workingflow_window.ui.wf_table.selectedItems()
        if len(select_items) > 0:
            # 去重
            selected_rows = set()
            for item in select_items:
                selected_rows.add(item.row())
            # 倒序排序
            selected_rows = sorted(selected_rows, reverse=True)
            # 删除
            for row in selected_rows:
                self.workingflow_window.ui.wf_table.removeRow(row)
            # 删除后选择一个删除区间的前一个元素
            if selected_rows[-1] - 1 >= 0:
                self.workingflow_window.ui.wf_table.setCurrentCell(selected_rows[-1] - 1, 0)

        self.wf_blockConnect = False

    def wf_overrideText(self):
        if self.wf_blockConnect == True:
            return

        self.wf_blockConnect = True

        cur_items = self.workingflow_window.ui.wf_table.selectedItems()
        if len(cur_items) == 1:
            item = cur_items[0]
            item_column = item.column()
            item_row = item.row()
            item_text = item.text().strip()
            if item_column == 0:
                # 标签更改：更新翻译
                translated_text = self.translateTag(item_text)
                translated_item = QTableWidgetItem(translated_text)
                self.workingflow_window.ui.wf_table.setItem(item_row, 1, translated_item)
                # 更改后保存当前页
            elif item_column == 1:
                # 翻译更改：更新翻译文件
                en_item = self.workingflow_window.ui.wf_table.item(item_row, 0)
                cn_item = self.workingflow_window.ui.wf_table.item(item_row, 1)
                if en_item is not None and cn_item is not None:
                    en_text = en_item.text().strip()
                    cn_text = cn_item.text().strip()
                    # 更新字典
                    self.update_translation(en_text, cn_text)
                    # 将翻译结果保存
                    self.write_translation_file()

        self.wf_blockConnect = False

        # 每一次更改内容都会进行保存
        self.wf_getTagAndTitle()
        self.wf_saveFile()

    def wf_SwitchPage(self, page):
        # 使用动态的方法使得储存的冗余信息尽可能少
        if page < 0:
            page = 0
        if page == self.wf_cur_page:
            # 前后页码一致，不对更改存储表格内容
            pass
        elif page > self.wf_cur_page:
            # 增页：先增页再保存
            while page > len(self.wf_spaceinfo) - 1:
                self.wf_spaceinfo.append([])
            while page > len(self.wf_spacename) - 1:
                self.wf_spacename.append('')
            self.wf_getTagAndTitle()
        elif page < self.wf_cur_page:
            # 删页：先保存后删除
            self.wf_getTagAndTitle()
            while (len(self.wf_spaceinfo) - 1 > page and
                   self.wf_spaceinfo[-1] == [] and
                   self.wf_spacename[-1] == ''):
                self.wf_spaceinfo.pop()
                self.wf_spacename.pop()

        # 调整完毕后即可将信息保存到字典
        self.wf_saveFile()
        # 更新页码信息
        self.wf_cur_page = page
        page_number_text = str(self.wf_cur_page + 1) + '/' + str(len(self.wf_spaceinfo))
        self.workingflow_window.ui.wf_pageShow.setText(page_number_text)
        # 删除当前内容
        self.workingflow_window.ui.wf_table.clearContents()
        self.workingflow_window.ui.wf_table.setRowCount(0)
        # 写入新的信息
        self.wf_loadTagAndTitle(page)
        # 更新上色状态
        self.wf_FontReset()
        # 切换页码后进行聚焦操作
        self.workingflow_window.ui.wf_table.setFocus()

    def wf_insertNewPage(self, page):
        # 新建页操作
        self.wf_spaceinfo.insert(page, [])
        self.wf_spacename.insert(page, '')
        self.wf_SwitchPage(page)

    def wf_delCurrentPage(self, page):
        # 删除页操作(删除当前页转到上一页)
        if 0 <= page < len(self.wf_spaceinfo):
            del self.wf_spaceinfo[page]
            del self.wf_spacename[page]
            self.wf_cur_page = self.wf_cur_page - 1
            self.wf_SwitchPage(page - 1)

    def wf_curEnItem(self):
        cur_items = self.workingflow_window.ui.wf_table.selectedItems()
        if len(cur_items) > 0:
            row = cur_items[0].row()
            en_item = self.workingflow_window.ui.wf_table.item(row, 0)
            return en_item
        else:
            return False

    def wf_EnterPressed(self):
        if self.workingflow_window.ui.wf_workmode.isChecked():
            en_item = self.wf_curEnItem()
            if en_item:
                self.wf_copy2tagTable(en_item.row(), en_item.column())
        else:
            # 编辑模式
            self.workingflow_window.ui.wf_table.editItem(
                self.workingflow_window.ui.wf_table.currentItem())

    def wf_copy2tagTable(self, row, col):
        if self.workingflow_window.ui.wf_workmode.isChecked():
            insert_text = self.workingflow_window.ui.wf_table.item(row, 0).text().strip()
            # 将其添加到tag_table
            if insert_text != '':
                self.addRow(text=insert_text)

    def wf_workingModeChanged(self):
        # 工作模式切换
        if self.workingflow_window.ui.wf_editmode.isChecked():
            # 编辑模式：允许更改，可以多选
            self.wf_workingMode = 'editing'
            self.workingflow_window.ui.wf_table.setEditTriggers(
                QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed | QAbstractItemView.AnyKeyPressed)
            self.workingflow_window.ui.wf_table.setSelectionBehavior(QAbstractItemView.SelectItems)
            self.workingflow_window.ui.wf_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
            # 分组名称：可编辑
            self.workingflow_window.ui.wf_insEdit.setReadOnly(False)
            # 允许编辑：加行、删行
            self.wf_blockConnect = False
            self.wf_blockAddRow = False
            self.wf_blockDeleteRow = False
            # 重载当前页刷新上色状态
            self.wf_FontReset()

        else:
            # 工作模式：不允许更改，点击复制，一次仅能选择一行
            self.wf_workingMode = 'working'
            self.workingflow_window.ui.wf_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.workingflow_window.ui.wf_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.workingflow_window.ui.wf_table.setSelectionMode(QAbstractItemView.SingleSelection)
            # 分组名称：只读
            self.workingflow_window.ui.wf_insEdit.setReadOnly(True)
            # 禁止加行、删行
            self.wf_blockConnect = True
            self.wf_blockAddRow = True
            self.wf_blockDeleteRow = True
            # 重载当前页刷新上色状态
            self.wf_FontReset()

        # 工作模式保存
        self.wf_saveFile()
        # 切换模式后聚焦操作
        self.workingflow_window.ui.wf_table.setFocus()