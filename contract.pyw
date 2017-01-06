#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from PyQt5.QtCore import (Qt, QCoreApplication, QTranslator, QDate,
                          QDateTime, QTimer)
from PyQt5.QtGui import QIcon, QFont, QDesktopServices
from PyQt5.QtWidgets import (QApplication, QDialog, QMainWindow,
                             QTreeWidgetItem, QHeaderView, QMessageBox)

import contract_rc
from ui_contract import *

from item import *

_translate = QCoreApplication.translate

class Contract(QMainWindow):
    def __init__(self, parent=None):
        super(Contract, self).__init__(parent)
        self.ui = Ui_Contract()
        self.ui.setupUi(self)
        
        self.addMenus()
        
        self.owner = QTreeWidgetItem(["xlongfeng肖龙峰"])
        self.ui.itemTreeWidget.addTopLevelItem(self.owner)
        
        self.ui.itemTreeWidget.setHeaderLabels([_translate('Contract', "Date"), \
                                                _translate('Contract', "Unit"), \
                                                _translate('Contract', "Name")])
        self.ui.itemTreeWidget.header().resizeSection(0, 128)
        self.ui.itemTreeWidget.header().resizeSection(1, 32)
        self.ui.itemTreeWidget.itemDoubleClicked.connect(self.editItem)
        self.loadItems()
    
    def addMenus(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu(_translate("Contract", "File"))
        fileMenu.addAction(_translate('Contract', 'New Database'), self.newDatabase)
        fileMenu.addAction(_translate('Contract', 'Open Database'), self.openDatabase)
        fileMenu.addAction(_translate('Contract', 'Exit'), QCoreApplication.instance().quit)
        
        itemMenu = menuBar.addMenu(_translate("Contract", "Item"))
        itemMenu.addAction(_translate('Contract', 'New Item'), self.newItem)
    
    def newDatabase(self):
        pass
    
    def openDatabase(self):
        pass
    
    def loadItems(self):
        for item in session.query(ItemModel).order_by(desc(ItemModel.startDate)):
            self.owner.addChild(QTreeWidgetItem([item.startDatetoString(), str(item.quantity) \
                                                 , item.name, str(item.id)]))
        self.owner.setExpanded(True)
    
    def newItem(self):
        dialog = ItemNewDialog(self)
        if dialog.exec() == QDialog.Accepted:
            item = dialog.item
            self.owner.addChild(QTreeWidgetItem([item.startDatetoString(), \
                                                 str(item.quantity), \
                                                 item.name, str(item.id)]))
            self.owner.sortChildren(0, Qt.DescendingOrder)
    
    def editItem(self, treeWidgetItem, column):
        if treeWidgetItem == self.owner:
            return
        dialog = ItemEditDialog(int(treeWidgetItem.text(3)), self)
        if dialog.exec() == QDialog.Accepted:
            if dialog.deleteItem:
                self.owner.takeChild(self.owner.indexOfChild(treeWidgetItem))
            else:
                item = dialog.item
                treeWidgetItem.setText(0, item.startDatetoString())
                treeWidgetItem.setText(1, str(item.quantity))
                treeWidgetItem.setText(2, str(item.name))
            self.owner.sortChildren(0, Qt.DescendingOrder)

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    
    app.setWindowIcon(QIcon(':/images/contract.png'))
    
    font = app.font()  
    font.setPointSize(10)
    app.setFont(font)
    
    translator = QTranslator(app)
    translator.load('Contract_zh_CN')
    app.installTranslator(translator)
    
    contract = Contract()
    contract.show()
    
    sys.exit(app.exec_())
