import json
import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from filterWindow import Ui_Filter
        
class Filters():
    def __init__(self):
        super().__init__()
        # 载入子窗口
        self.filter_window = QWidget()
        self.filter_window.ui = Ui_Filter()
        self.filter_window.ui.setupUi(self.filter_window)
        
        # Enter
        QShortcut(QKeySequence(Qt.Key_Enter), self.filter_window) \
            .activated.connect(self.addFilterRow)
        QShortcut(QKeySequence(Qt.Key_Return), self.filter_window) \
            .activated.connect(self.addFilterRow)
        # Ctrl + Enter：确认操作
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Enter), self.filter_window) \
            .activated.connect(self.confirmFilter)
        QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Return), self.filter_window) \
            .activated.connect(self.confirmFilter)
        # Del
        QShortcut(QKeySequence(Qt.Key_Delete), self.filter_window) \
            .activated.connect(self.deleteFilterRow)
        # Esc  
        QShortcut(QKeySequence(Qt.Key_Escape), self.filter_window) \
            .activated.connect(self.filter_window.close)
        # Left：切换到标签过滤列表
        QShortcut(QKeySequence(Qt.Key_Left), self.filter_window) \
            .activated.connect(lambda: self.filter_window.ui.tagFilterbutton.setChecked(True))
        # Right：切换到图片过滤列表
        QShortcut(QKeySequence(Qt.Key_Right), self.filter_window) \
            .activated.connect(lambda: self.filter_window.ui.imageFilterbutton.setChecked(True))
            
        # 过滤器:标签过滤、图片过滤按钮对应两页
        self.filter_window.ui.pushbuttonGroup.buttonToggled.connect(self.FilterPageChanged)
        # 过滤器:黑白名单对应过滤模式
        self.filter_window.ui.radiobuttonGroup.buttonToggled.connect(self.FilterModeChanged)
        # 过滤器:添加
        self.filter_window.ui.filter_add.clicked.connect(self.addFilterRow)
        # 过滤器:删除
        self.filter_window.ui.filter_del.clicked.connect(self.deleteFilterRow)
        # 过滤器:确认
        self.filter_window.ui.filter_ok.clicked.connect(self.confirmFilter)
        # 过滤器:取消
        self.filter_window.ui.filter_cancel.clicked.connect(self.filter_window.close)

        # fullInfo是一个嵌套字典，储存着不同工作路径下的全套信息
        self.fullInfo = {}
        self.tagBlacklist = []
        self.tagWhitelist = []
        self.imageBlacklist = []
        self.imageWhitelist = []
        self.filterLabelContents = {
            'tag-black':'隐藏下表的标签',
            'tag-white':'仅显示下表的标签',
            'image-black':'筛除包含下表标签的图像',
            'image-white':'仅显示包含下表标签的图像'
        }
        # 使用6个变量维护过滤器
        # 过滤内容的加载与保存依赖lastfullfilterState和curfullfilterState
        # 过滤器应用到标签列表依赖于curfilterPage、curtagfilterMode和curimagefilterMode
        self.lastfullfilterState = ''
        self.curfullfilterState = 'tag-black'
        self.curfilterPage = 'tag'
        self.curtagfilterMode = 'black'
        self.curimagefilterMode = 'black'
        self.blockFiltermodeChangedConnect = False
    
    # -------------------
    #
    # 读取与写入
    #
    # -------------------
    
    def loadInfofromFile(self):
        try:
            # 载入4个字典
            with open('./filtercache/filterinfo.txt', 'r') as f:
                self.fullInfo = json.load(f)

            cur_fullInfo = self.fullInfo[self.folder_path]
            self.curfilterPage = cur_fullInfo['curfilterPage']
            self.curtagfilterMode = cur_fullInfo['curtagfilterMode']
            self.curimagefilterMode = cur_fullInfo['curimagefilterMode']
            self.tagBlacklist = cur_fullInfo['tagBlacklist']
            self.tagWhitelist = cur_fullInfo['tagWhitelist']
            self.imageBlacklist = cur_fullInfo['imageBlacklist']
            self.imageWhitelist = cur_fullInfo['imageWhitelist']
        except:
            pass
    
    def saveInfo2File(self):
        self.fullInfo[self.folder_path] = {
            'curfilterPage':self.curfilterPage,
            'curtagfilterMode':self.curtagfilterMode,
            'curimagefilterMode':self.curimagefilterMode,
            'tagBlacklist':self.tagBlacklist,
            'tagWhitelist':self.tagWhitelist,
            'imageBlacklist':self.imageBlacklist,
            'imageWhitelist':self.imageWhitelist
        }
        
        if not os.path.exists('./filtercache'):
            os.makedirs('./filtercache')
        with open('./filtercache/filterinfo.txt', 'w') as f:
            json.dump(self.fullInfo, f)
            
    def loadFiltertag2Table(self):
        # 获取当前对应的过滤列表
        if self.curfullfilterState == 'tag-black':
            filter_list = self.tagBlacklist
        elif self.curfullfilterState == 'tag-white':
            filter_list = self.tagWhitelist
        elif self.curfullfilterState == 'image-black':
            filter_list = self.imageBlacklist
        elif self.curfullfilterState == 'image-white':
            filter_list = self.imageWhitelist
        # 写入
        for tag in filter_list:
            rowPosition = self.filter_window.ui.filtertable.rowCount()
            self.filter_window.ui.filtertable.insertRow(rowPosition)
            self.filter_window.ui.filtertable.setItem(rowPosition, 0, QTableWidgetItem(tag))   
    
    def saveFiltetag2Dict(self):
        if self.lastfullfilterState == '':
            return
        # 获取列表
        filter_list = self.getFiltertagfromTable()
        # 将内容保存到相应字典
        if self.lastfullfilterState == 'tag-black':
            self.tagBlacklist = filter_list
        elif self.lastfullfilterState == 'tag-white':
            self.tagWhitelist = filter_list
        elif self.lastfullfilterState == 'image-black':
            self.imageBlacklist = filter_list
        elif self.lastfullfilterState == 'image-white':
            self.imageWhitelist = filter_list
            
        # 保存字典到文件
        self.saveInfo2File()
    
    # -------------------
    #
    # 表内操作
    #
    # -------------------
    
    def FilterPageChanged(self):
        
        self.blockFiltermodeChangedConnect = True
        # 获取当前状态
        if self.filter_window.ui.tagFilterbutton.isChecked():
            self.curfilterPage = 'tag'
            if self.curtagfilterMode == 'black':
                self.filter_window.ui.filter_useBlacklist.setChecked(True)
            else:
                self.filter_window.ui.filter_useWhitelist.setChecked(True)
        else:
            self.curfilterPage = 'image'
            if self.curimagefilterMode == 'black':
                self.filter_window.ui.filter_useBlacklist.setChecked(True)
            else:
                self.filter_window.ui.filter_useWhitelist.setChecked(True)

        self.blockFiltermodeChangedConnect = False
        
        self.FilterModeChanged()
    
    def FilterModeChanged(self):
        if self.blockFiltermodeChangedConnect == True:
            return
        
        # 状态处理
        self.lastfullfilterState = self.curfullfilterState
        if self.curfilterPage == 'tag':
            if self.filter_window.ui.filter_useBlacklist.isChecked():
                # 标签过滤，黑名单
                self.curfullfilterState = 'tag-black'
                self.curtagfilterMode = 'black'
            else:
                # 标签过滤，白名单
                self.curfullfilterState = 'tag-white'
                self.curtagfilterMode = 'white'
        elif self.curfilterPage == 'image':
            if self.filter_window.ui.filter_useBlacklist.isChecked():
                # 图片过滤，黑名单
                self.curfullfilterState = 'image-black'
                self.curimagefilterMode = 'black'
            else:
                # 图片过滤，白名单
                self.curfullfilterState = 'image-white'
                self.curimagefilterMode = 'white'
            
        # 执行保存操作
        self.saveFiltetag2Dict()
        # 清空表格
        self.filter_window.ui.filtertable.clearContents()
        self.filter_window.ui.filtertable.setRowCount(0)
        # 更改说明
        self.filter_window.ui.filter_label.setText(self.filterLabelContents[self.curfullfilterState])
        # 载入过滤内容到表格
        self.loadFiltertag2Table()
        # 执行聚焦操作
        self.filter_window.ui.filtertable.setFocus()
        # 如果有内容，就选择最后一个项
        if self.filter_window.ui.filtertable.rowCount() > 0:
            self.filter_window.ui.filtertable.setCurrentCell(self.filter_window.ui.filtertable.rowCount() - 1, 0)
    
    def addFilterRow(self):
        # 添加一个空行到表格
        self.filter_window.ui.filtertable.clearSelection()
        row = self.filter_window.ui.filtertable.rowCount()
        self.filter_window.ui.filtertable.insertRow(row)
        item = QTableWidgetItem('')
        self.filter_window.ui.filtertable.setItem(row, 0, item)
        self.filter_window.ui.filtertable.setCurrentCell(row, 0)

    def deleteFilterRow(self):
        # 删除选中的行
        select_items = self.filter_window.ui.filtertable.selectedItems()
        if len(select_items) > 0:
            selected_rows = set()
            for item in select_items:
                selected_rows.add(item.row())
            # 排序
            selected_rows = sorted(selected_rows, reverse=True)
            # 删除
            for row in selected_rows:
                self.filter_window.ui.filtertable.removeRow(row)
            # 删除后选择一个删除区间的前一个元素
            if selected_rows[-1] - 1 >= 0:
                self.filter_window.ui.filtertable.setCurrentCell(selected_rows[-1] - 1, 0)
    
    def confirmFilter(self):
        # 保存并关闭
        self.saveFiltetag2Dict()
        self.filter_window.close()
        # 将4个过滤器应用到主窗口
        self.applyFilter2mainWindow(filterimage=True)
        
    def getFiltertagfromTable(self):
        # 读取表格中的内容
        filter_list = []
        for row in range(self.filter_window.ui.filtertable.rowCount()):
            item = self.filter_window.ui.filtertable.item(row, 0)
            if item.text() != '':
                filter_list.append(item.text().strip())
        return filter_list     
                
    
    # -------------------
    #
    # 菜单--过滤器操作函数
    #
    # -------------------
    
    def open_Filter(self):
        if self.ui.openFilter.isEnabled():
            # 这个相当于载入状态
            self.FilterPageChanged()
            # 显示窗口
            self.filter_window.show()
    
    def clearFilterConfirm(self, title, msg):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        reply = msg_box.exec_()

        if reply == QMessageBox.Yes:
            return True
        elif reply == QMessageBox.No:
            return False
        
        return False
    
    def clear_Filter(self):
        if self.clearFilterConfirm(title='操作确认',msg='清空过滤器？') == True:
            self.tagBlacklist = []
            self.tagWhitelist = []
            self.imageBlacklist = []
            self.imageWhitelist = []
            self.curfilterPage = 'tag'
            self.curtagfilterMode = 'white'
            self.curimagefilterMode = 'white'
            # 空的白名单等于都显示
            self.applyFilter2mainWindow(filterimage=True)
            # 再变回黑名单
            self.curtagfilterMode = 'black'
            self.curimagefilterMode = 'black'
            # 要删除过滤器列表上遗留的内容
            self.filter_window.ui.filtertable.clearContents()
            self.filter_window.ui.filtertable.setRowCount(0)
            # 最后保存
            self.saveInfo2File()
    
    # -------------------
    #
    # 事后操作
    #
    # -------------------

    def applyFilter2mainWindow(self, filterimage=False):
        # filterimage：是否应用图片筛选
        if filterimage == True:
            if self.curimagefilterMode == 'black':
                # 应用黑名单
                self.imageBlacklist_Filter()
            elif self.curimagefilterMode == 'white':
                # 应用白名单
                self.imageWhitelist_Filter()
        # 对标签的过滤始终执行
        if self.curtagfilterMode == 'black':
            self.tagBlacklist_Filter()
        elif self.curtagfilterMode == 'white':
            self.tagWhitelist_Filter()

    def tagBlacklist_Filter(self):
        for row in range(self.ui.tagTable.rowCount()):
            item = self.ui.tagTable.item(row, 0)
            if item and item.text() != '':
                tag = item.text()
                # 黑名单：默认不隐藏，查找需要隐藏的标签
                row_hidden = False
                for filter_tag in self.tagBlacklist: 
                    if filter_tag in tag:
                        row_hidden = True
                        break
                self.ui.tagTable.setRowHidden(row, row_hidden)


    def tagWhitelist_Filter(self):
        for row in range(self.ui.tagTable.rowCount()):
            item = self.ui.tagTable.item(row, 0)
            if item and item.text() != '':
                tag = item.text()
                # 白名单：默认隐藏，查找需要显示的标签
                row_hidden = True
                for filter_tag in self.tagWhitelist:
                    if filter_tag in tag:
                        row_hidden = False
                        break
                # 如果白名单什么都没有，就是都显示的意思
                if len(self.tagWhitelist) == 0:
                    row_hidden = False
                self.ui.tagTable.setRowHidden(row, row_hidden)
        
    def imageBlacklist_Filter(self):
        # 第一层：遍历图片列表
        for image_row in range(self.ui.imageList.count()):
            item = self.ui.imageList.item(image_row)
            if item and item.text() != '':
                # 重新从文件读取标签
                image_filename = item.text()
                tags_filename = image_filename.replace(".jpg", ".txt").replace(".png", ".txt")
                tags = self.loadTagsfromFile(tags_filename)
                
                row_hidden = False
                
                # 第二层：遍历标签列表
                for tag in tags:
                    # 第三层：遍历过滤器列表
                    for filter_tag in self.imageBlacklist:
                        if filter_tag in tag:
                            row_hidden = True
                            break
                    if row_hidden == True:
                        break
                
                # 如果当前选择的图片将要被隐藏
                if row_hidden == True and item.isSelected():
                    # 询问是否保存
                    if self.ui.saveConfirm.isChecked():
                        # 弹出一个强制选择窗口
                        self.SaveConfirm_2opt(title='保存确认',msg='该图片将被隐藏，是否保存？')
                    else:
                        # 如果不询问默认保存
                        self.saveTags2File()
                    # 关闭预览图
                    if self.imageShowed == True:
                        self.switch_image_preview()
                    # 清空表格
                    self.ui.tagTable.clearContents()
                    self.ui.tagTable.setRowCount(0)
                    
                item.setHidden(row_hidden)

    def imageWhitelist_Filter(self):
        for image_row in range(self.ui.imageList.count()):
            item = self.ui.imageList.item(image_row)
            if item and item.text() != '':
                image_filename = item.text()
                tags_filename = image_filename.replace(".jpg", ".txt").replace(".png", ".txt")
                tags = self.loadTagsfromFile(tags_filename)
                row_hidden = True
                for tag in tags:
                    for filter_tag in self.imageWhitelist:
                        if filter_tag in tag:
                            row_hidden = False
                            break
                    if row_hidden == False:
                        break
                        
                # 过滤列表为空，默认都显示
                if len(self.imageWhitelist) == 0:
                    row_hidden = False
                
                if row_hidden == True and item.isSelected():
                    if self.ui.saveConfirm.isChecked():
                        self.SaveConfirm_2opt(title='保存确认',msg='该图片将被隐藏，是否保存？')
                    else:
                        self.saveTags2File()
                        
                    if self.imageShowed == True:
                        self.switch_image_preview()
                        
                    self.ui.tagTable.clearContents()
                    self.ui.tagTable.setRowCount(0)
                
                item.setHidden(row_hidden)
