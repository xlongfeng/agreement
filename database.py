#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from PyQt5.QtCore import (Qt, QObject, QCoreApplication, QDate,
                          QDir, QFileInfo)
from PyQt5.QtWidgets import (QDialog, QListWidgetItem, \
                             QAction, QMessageBox)

from ui_databaseview import *

_translate = QCoreApplication.translate

Base = declarative_base()

class Database(QObject):
    pInstance = None
    _name = None
    _session = None

    def __init__(self, parent=None):
        super(Database, self).__init__(parent)
    
    @classmethod
    def instance(cls):
        if cls.pInstance is None:
            cls.pInstance = cls()
        return cls.pInstance
    
    def open(self, name):
        self._name = name
        engine = create_engine("sqlite:///{}.sqlite".format(name))
        Base.metadata.create_all(engine)
        self._session = sessionmaker(engine)()
    
    def name(self):
        return self._name
    
    def session(self):
        return self._session
    
    def isExist(self, name):
        return QFileInfo.exists("{}.sqlite".format(name))

class DatabaseDialog(QDialog):
    def __init__(self, parent=None):
        super(DatabaseDialog, self).__init__(parent)
        self.ui = Ui_DatabaseView()
        self.ui.setupUi(self)
        self.ui.cancelPushButton.pressed.connect(self.reject)
        
        self.loadDatabase()
    
    def loadDatabase(self):
        dir = QDir(".")
        for entry in dir.entryInfoList(["*.sqlite"], QDir.Files):
            self.ui.databaseListWidget.addItem(entry.baseName())

class NewDatabaseDialog(DatabaseDialog):
    def __init__(self, parent=None):
        super(NewDatabaseDialog, self).__init__(parent)
        self.ui.openPushButton.setVisible(False)
        self.ui.newPushButton.pressed.connect(self.createDb)
    
    def createDb(self):
        name = self.ui.databaseLineEdit.text()
        if name == "":
            pass
        elif Database.instance().isExist(name):
            QMessageBox.warning(self, "", _translate("DatabaseDialog", "Existing {} Database").format(name))
        else:
            Database.instance().open(name)
            self.accept()

class OpenDatabaseDialog(DatabaseDialog):
    def __init__(self, parent=None):
        super(OpenDatabaseDialog, self).__init__(parent)
        self.ui.databaseListWidget.itemDoubleClicked.connect(self.openDb)
        self.ui.databaseLabel.setVisible(False)
        self.ui.databaseLineEdit.setVisible(False)
        self.ui.newPushButton.setVisible(False)
        self.ui.openPushButton.pressed.connect(self.openDb)
    
    def openDb(self, item = None):
        if item is None:
            items = self.ui.databaseListWidget.selectedItems()
            if len(items) == 0:
                return
            else:
                item = items[0]
        name = item.text()
        Database.instance().open(name)
        self.accept()