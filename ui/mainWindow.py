# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(886, 677)
        mainWindow.setStyleSheet("* {\n"
"    font-family:\"KaiTi\";\n"
"    font-size:28px;\n"
"    color: #F8F8F2;\n"
"}\n"
"\n"
"*::item:hover {\n"
"    background-color: #474844;\n"
"}\n"
"*::item:selected {\n"
"    background-color: #75715E;\n"
"}\n"
"/* 背景 */\n"
"QWidget {\n"
"    background-color: #202120;\n"
"}\n"
"/* list */\n"
"QListWidget {\n"
"    background-color: #272822;\n"
"    border: none;\n"
"}\n"
"QListWidget::item {\n"
"    padding: 5px;\n"
"}\n"
"/* table */\n"
"QTableWidget {\n"
"    background-color: #272822;\n"
"    border: none;\n"
"}\n"
"QTableWidget::item {\n"
"    \n"
"}\n"
"/* table:表头 */\n"
"QHeaderView::section {\n"
"    background-color: #272822;\n"
"}\n"
"/* 按钮 */\n"
"QPushButton {\n"
"    background-color: #75715e;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #8d8871;\n"
"}\n"
"QPushButton:selected {\n"
"    background-color: #8d8871;\n"
"}\n"
"/* 多页Tab */\n"
"QTabBar::tab {\n"
"    background-color: #34352f;\n"
"    margin-right:1px;\n"
"    margin-left:1px;\n"
"    width:150px;\n"
"}\n"
"QTabBar::tab:selected {\n"
"    background-color: #272822;\n"
"}\n"
"QTabWidget::pane{\n"
"    border:none;\n"
"}\n"
"/* 状态条 */\n"
"QStatusBar {\n"
"    background-color: #414339;\n"
"}\n"
"/* 菜单栏 */\n"
"QMenuBar, QMenu {\n"
"    font-family:\"SimHei\";\n"
"    font-size:25px;\n"
"    color: #F8F8F2;\n"
"}\n"
"QMenuBar::item:disabled, QMenu::item:disabled {\n"
"    color: #4c4d4b;\n"
"}\n"
"/* 滑动条 */\n"
"QScrollBar:disabled {\n"
"    background: #272822;\n"
"}\n"
"QScrollBar:vertical {\n"
"    width: 8px;\n"
"}\n"
"QScrollBar:horizontal {\n"
"    height: 8px;\n"
"}\n"
"QScrollBar::handle { \n"
"    padding: 0;\n"
"    margin: 2px;\n"
"    border-radius: 2px;\n"
"    border: 2px solid palette(midlight);\n"
"    background: palette(midlight);\n"
"}\n"
"QScrollBar::handle:vertical {\n"
"    min-height: 20px;\n"
"    min-width: 0px;\n"
"}\n"
"QScrollBar::handle:horizontal {\n"
"    min-width: 20px;\n"
"    min-height: 0px;\n"
"}\n"
"QScrollBar::handle:hover {\n"
"    border-color: palette(light);\n"
"    background: palette(light);\n"
"}\n"
"QScrollBar::handle:pressed {\n"
"    background: palette(highlight);\n"
"    border-color: palette(highlight);\n"
"}\n"
"QScrollBar::add-line , QScrollBar::sub-line {\n"
"    height: 0px;\n"
"    border: 0px;\n"
"}\n"
"QScrollBar::up-arrow, QScrollBar::down-arrow {\n"
"    border: 0px;\n"
"    width: 0px;\n"
"    height: 0px;\n"
"}\n"
"QScrollBar::add-page, QScrollBar::sub-page {\n"
"    background: none;\n"
"}")
        self.centralwidget = QtWidgets.QWidget(mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.imageTable = QtWidgets.QTableWidget(self.centralwidget)
        self.imageTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.imageTable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.imageTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.imageTable.setObjectName("imageTable")
        self.imageTable.setColumnCount(2)
        self.imageTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.imageTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.imageTable.setHorizontalHeaderItem(1, item)
        self.imageTable.horizontalHeader().setCascadingSectionResizes(False)
        self.imageTable.horizontalHeader().setDefaultSectionSize(150)
        self.imageTable.horizontalHeader().setMinimumSectionSize(50)
        self.imageTable.horizontalHeader().setStretchLastSection(True)
        self.imageTable.verticalHeader().setVisible(False)
        self.imageTable.verticalHeader().setDefaultSectionSize(150)
        self.imageTable.verticalHeader().setHighlightSections(False)
        self.imageTable.verticalHeader().setMinimumSectionSize(150)
        self.horizontalLayout.addWidget(self.imageTable)
        self.tagTable = QtWidgets.QTableWidget(self.centralwidget)
        self.tagTable.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.EditKeyPressed)
        self.tagTable.setObjectName("tagTable")
        self.tagTable.setColumnCount(2)
        self.tagTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tagTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tagTable.setHorizontalHeaderItem(1, item)
        self.tagTable.horizontalHeader().setCascadingSectionResizes(True)
        self.tagTable.horizontalHeader().setDefaultSectionSize(10)
        self.tagTable.horizontalHeader().setMinimumSectionSize(10)
        self.tagTable.horizontalHeader().setSortIndicatorShown(True)
        self.tagTable.horizontalHeader().setStretchLastSection(True)
        self.tagTable.verticalHeader().setVisible(False)
        self.tagTable.verticalHeader().setHighlightSections(False)
        self.horizontalLayout.addWidget(self.tagTable)
        self.copyList = QtWidgets.QListWidget(self.centralwidget)
        self.copyList.setObjectName("copyList")
        self.horizontalLayout.addWidget(self.copyList)
        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 4)
        self.horizontalLayout.setStretch(2, 2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        mainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(mainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 886, 31))
        self.menubar.setObjectName("menubar")
        self.File = QtWidgets.QMenu(self.menubar)
        self.File.setFocusPolicy(QtCore.Qt.NoFocus)
        self.File.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.File.setObjectName("File")
        self.Utils = QtWidgets.QMenu(self.menubar)
        self.Utils.setObjectName("Utils")
        self.Settings = QtWidgets.QMenu(self.menubar)
        self.Settings.setObjectName("Settings")
        self.savemode = QtWidgets.QMenu(self.Settings)
        self.savemode.setObjectName("savemode")
        mainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(mainWindow)
        self.statusbar.setObjectName("statusbar")
        mainWindow.setStatusBar(self.statusbar)
        self.openFile = QtWidgets.QAction(mainWindow)
        self.openFile.setCheckable(False)
        self.openFile.setObjectName("openFile")
        self.saveFile = QtWidgets.QAction(mainWindow)
        self.saveFile.setEnabled(False)
        self.saveFile.setObjectName("saveFile")
        self.keepOrder = QtWidgets.QAction(mainWindow)
        self.keepOrder.setCheckable(True)
        self.keepOrder.setChecked(True)
        self.keepOrder.setObjectName("keepOrder")
        self.sortOrder = QtWidgets.QAction(mainWindow)
        self.sortOrder.setCheckable(True)
        self.sortOrder.setObjectName("sortOrder")
        self.action_2 = QtWidgets.QAction(mainWindow)
        self.action_2.setCheckable(True)
        self.action_2.setChecked(True)
        self.action_2.setObjectName("action_2")
        self.tagBlacklist = QtWidgets.QAction(mainWindow)
        self.tagBlacklist.setEnabled(False)
        self.tagBlacklist.setObjectName("tagBlacklist")
        self.imageBlacklist = QtWidgets.QAction(mainWindow)
        self.imageBlacklist.setEnabled(False)
        self.imageBlacklist.setObjectName("imageBlacklist")
        self.tagWhitelist = QtWidgets.QAction(mainWindow)
        self.tagWhitelist.setEnabled(False)
        self.tagWhitelist.setObjectName("tagWhitelist")
        self.imageWhitelist = QtWidgets.QAction(mainWindow)
        self.imageWhitelist.setEnabled(False)
        self.imageWhitelist.setObjectName("imageWhitelist")
        self.openFilter = QtWidgets.QAction(mainWindow)
        self.openFilter.setEnabled(False)
        self.openFilter.setObjectName("openFilter")
        self.imageFilter = QtWidgets.QAction(mainWindow)
        self.imageFilter.setObjectName("imageFilter")
        self.clearFilter = QtWidgets.QAction(mainWindow)
        self.clearFilter.setEnabled(False)
        self.clearFilter.setObjectName("clearFilter")
        self.openWorkingFlow = QtWidgets.QAction(mainWindow)
        self.openWorkingFlow.setEnabled(False)
        self.openWorkingFlow.setObjectName("openWorkingFlow")
        self.saveConfirm = QtWidgets.QAction(mainWindow)
        self.saveConfirm.setCheckable(True)
        self.saveConfirm.setChecked(True)
        self.saveConfirm.setObjectName("saveConfirm")
        self.showImg = QtWidgets.QAction(mainWindow)
        self.showImg.setCheckable(True)
        self.showImg.setObjectName("showImg")
        self.oriorder_front = QtWidgets.QAction(mainWindow)
        self.oriorder_front.setCheckable(True)
        self.oriorder_front.setChecked(True)
        self.oriorder_front.setObjectName("oriorder_front")
        self.oriorder_behind = QtWidgets.QAction(mainWindow)
        self.oriorder_behind.setCheckable(True)
        self.oriorder_behind.setObjectName("oriorder_behind")
        self.sortorder = QtWidgets.QAction(mainWindow)
        self.sortorder.setCheckable(True)
        self.sortorder.setObjectName("sortorder")
        self.batchOperation = QtWidgets.QAction(mainWindow)
        self.batchOperation.setEnabled(False)
        self.batchOperation.setObjectName("batchOperation")
        self.File.addAction(self.openFile)
        self.File.addAction(self.saveFile)
        self.Utils.addAction(self.openFilter)
        self.Utils.addAction(self.openWorkingFlow)
        self.Utils.addAction(self.batchOperation)
        self.savemode.addAction(self.oriorder_front)
        self.savemode.addAction(self.oriorder_behind)
        self.savemode.addAction(self.sortorder)
        self.Settings.addAction(self.savemode.menuAction())
        self.Settings.addAction(self.saveConfirm)
        self.menubar.addAction(self.File.menuAction())
        self.menubar.addAction(self.Utils.menuAction())
        self.menubar.addAction(self.Settings.menuAction())

        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "标签编辑器"))
        item = self.imageTable.horizontalHeaderItem(0)
        item.setText(_translate("mainWindow", "缩略图"))
        item = self.imageTable.horizontalHeaderItem(1)
        item.setText(_translate("mainWindow", "名称"))
        item = self.tagTable.horizontalHeaderItem(0)
        item.setText(_translate("mainWindow", "英文标签"))
        item = self.tagTable.horizontalHeaderItem(1)
        item.setText(_translate("mainWindow", "中文标签"))
        self.File.setTitle(_translate("mainWindow", "文件"))
        self.Utils.setTitle(_translate("mainWindow", "工具"))
        self.Settings.setTitle(_translate("mainWindow", "设置"))
        self.savemode.setTitle(_translate("mainWindow", "保存模式"))
        self.openFile.setText(_translate("mainWindow", "打开文件夹"))
        self.saveFile.setText(_translate("mainWindow", "保存"))
        self.keepOrder.setText(_translate("mainWindow", "保持原始顺序"))
        self.sortOrder.setText(_translate("mainWindow", "按照字母排序"))
        self.action_2.setText(_translate("mainWindow", "切换图片保存确认"))
        self.tagBlacklist.setText(_translate("mainWindow", "黑名单"))
        self.imageBlacklist.setText(_translate("mainWindow", "黑名单"))
        self.tagWhitelist.setText(_translate("mainWindow", "白名单"))
        self.imageWhitelist.setText(_translate("mainWindow", "白名单"))
        self.openFilter.setText(_translate("mainWindow", "过滤器    Ctrl+F"))
        self.imageFilter.setText(_translate("mainWindow", "图片过滤"))
        self.clearFilter.setText(_translate("mainWindow", "清空过滤器"))
        self.openWorkingFlow.setText(_translate("mainWindow", "工作流    Ctrl+W"))
        self.saveConfirm.setText(_translate("mainWindow", "询问是否保存"))
        self.showImg.setText(_translate("mainWindow", "显示缩略图"))
        self.oriorder_front.setText(_translate("mainWindow", "原始顺序(前插)"))
        self.oriorder_behind.setText(_translate("mainWindow", "原始顺序(后插)"))
        self.sortorder.setText(_translate("mainWindow", "按照字母排序"))
        self.batchOperation.setText(_translate("mainWindow", "批量增删  Ctrl+B"))