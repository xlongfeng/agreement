#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from enum import Enum
import json

import sqlalchemy
from sqlalchemy import (Column, ForeignKey, Integer, \
                        String, Date, UnicodeText, \
                        create_engine, desc)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base

from PyQt5.QtCore import Qt, QCoreApplication, QDate
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QVBoxLayout, \
                             QFormLayout, QWidget, QLabel, QGroupBox, \
                             QSpinBox, QLineEdit, QHeaderView, QTreeWidgetItem, \
                             QAction, QMessageBox)
from PyQt5.QtGui import QIntValidator

from ui_itemview import *
from ui_itemphaseview import *
from ui_itemdualphasenewview import *

_translate = QCoreApplication.translate

Base = declarative_base()

def qdate_to_date(qdate):
    return datetime.strptime(qdate.toString("yyyy-MM-dd"), "%Y-%m-%d").date()

class ItemModel(Base):
    __tablename__ = 'agreement_item'
    
    id = Column(Integer, primary_key=True)
    createDate =  Column('create_date', Date)
    writeDate =  Column('write_date', Date)
    
    name = Column('name', String)
    startDate =  Column('start_date', Date)
    quantity = Column('quantity', Integer)
    
    checkin = Column('checkin', Integer)
    checkout = Column('checkout', Integer)
    fee = Column('fee', Integer)
    
    period = Column('period', Integer)
    
    markup = Column('markup', String)
    cashOut = Column('cash_out', String)
    dualPhase = Column('dual_phase', String)
    
    note = Column('note', UnicodeText)
    
    def startDatetoString(self):
        return self.startDate.strftime("%Y-%m-%d")

    def getMarkup(self):
        if self.markup is not None and self.markup != "":
            markup = json.loads(self.markup)
            markup = sorted(markup, key=lambda x: x["phase"])
        else:
            markup = []
        return markup
    
    def setMarkup(self, markup):
        self.markup = json.dumps(markup)
    
    def getCashOut(self):
        if self.cashOut is not None and self.cashOut != "":
            cashOut = json.loads(self.cashOut)
            cashOut = sorted(cashOut)
        else:
            cashOut = []
        return cashOut
    
    def setCashOut(self, cashOut):
        self.cashOut = json.dumps(cashOut)
    
    def getCashOutAmount(self, phase):
        return (phase - 1) * self.checkout + (self.period - phase - 1) * self.checkin
    
    def getDualPhase(self):
        if self.dualPhase is not None and self.dualPhase != "":
            dualPhase = json.loads(self.dualPhase)
            dualPhase = sorted(dualPhase, key=lambda x: x["date"])
        else:
            dualPhase = []
        return dualPhase
    
    def setDualPhase(self, dualPhase):
        self.dualPhase = json.dumps(dualPhase)

engine = create_engine('sqlite:///storage.sqlite')
Base.metadata.create_all(engine)

session = sessionmaker(engine)()

class ItemDualPhaseNewDialog(QDialog):
    def __init__(self, item, dualPhaseEdit, parent=None):
        super(ItemDualPhaseNewDialog, self).__init__(parent)
        self.ui = Ui_ItemDualPhaseNewView()
        self.ui.setupUi(self)
        
        self.item = item
        minDate = item.startDate
        maxDate = item.startDate + timedelta(days=item.period * 31)
        self.ui.dateEdit.setDateRange(minDate, maxDate)
        
        self.monthCheckBox = list()
        self.monthCheckBox.append(self.ui.m1CheckBox)
        self.monthCheckBox.append(self.ui.m2CheckBox)
        self.monthCheckBox.append(self.ui.m3CheckBox)
        self.monthCheckBox.append(self.ui.m4CheckBox)
        self.monthCheckBox.append(self.ui.m5CheckBox)
        self.monthCheckBox.append(self.ui.m6CheckBox)
        self.monthCheckBox.append(self.ui.m7CheckBox)
        self.monthCheckBox.append(self.ui.m8CheckBox)
        self.monthCheckBox.append(self.ui.m9CheckBox)
        self.monthCheckBox.append(self.ui.m10CheckBox)
        self.monthCheckBox.append(self.ui.m11CheckBox)
        self.monthCheckBox.append(self.ui.m12CheckBox)
        
        self.dualPhaseEdit = dualPhaseEdit
        self.loadDualPhase()
        self.ui.savePushButton.pressed.connect(self.onAccepted)
        self.ui.cancelPushButton.pressed.connect(self.reject)
    
    def loadDualPhase(self):
        if self.dualPhaseEdit is None:
            return
        
        self.ui.dateEdit.setDate(QDate.fromString(self.dualPhaseEdit["date"], Qt.ISODate))
        for i in range(0, 12):
            if (i + 1) in self.dualPhaseEdit["months"]:
                self.monthCheckBox[i].setChecked(True)
    
    def monthHasChecked(self):
        hasChecked = False
        for checkBox in self.monthCheckBox:
            if checkBox.isChecked():
                hasChecked = True
                break;
        return hasChecked
    
    def getDualPhase(self):
        months = list()
        for i in range(0, 12):
            if self.monthCheckBox[i].isChecked():
                months.append(i + 1)
        return dict(date=qdate_to_date(self.ui.dateEdit.date()).isoformat(),
                    months=months)
    
    def onAccepted(self):
        if self.monthHasChecked() == False:
            QMessageBox.warning(self, "", _translate("ItemViewDialog", "No month was checked"))
            return
        
        dualPhase = self.item.getDualPhase()
        for dp in dualPhase:
            if dp["date"] == self.getDualPhase()["date"] and self.dualPhaseEdit is None:
                QMessageBox.warning(self, "", _translate("ItemViewDialog", "Duplicate date"))
                return
        
        if self.dualPhaseEdit is not None:
            dualPhase.remove(self.dualPhaseEdit)
        dualPhase.append(self.getDualPhase())
        self.item.setDualPhase(dualPhase)
        self.accept()

class ItemMarkupNewDialog(QDialog):
    def __init__(self, item, markupEdit, parent=None):
        super(ItemMarkupNewDialog, self).__init__(parent)
        self.ui = Ui_ItemPhaseView()
        self.ui.setupUi(self)
        self.setWindowTitle(_translate("ItemPhaseView", "New Markup"))
        
        self.item = item
        
        self.ui.phaseSpinBox.setRange(1, item.period)
        self.ui.amountLineEdit.setValidator(QIntValidator(self))
        
        self.markupEdit = markupEdit
        self.loadMarkupEdit()
        self.ui.savePushButton.pressed.connect(self.onAccepted)
        self.ui.cancelPushButton.pressed.connect(self.reject)
    
    def loadMarkupEdit(self):
        if self.markupEdit is None:
            return
        
        self.ui.phaseSpinBox.setValue(self.markupEdit["phase"])
        self.ui.amountLineEdit.setText(str(self.markupEdit["amount"]))
    
    def getMarkup(self):
        return dict(phase=self.ui.phaseSpinBox.value(), amount=int(self.ui.amountLineEdit.text()))
    
    def onAccepted(self):
        if self.ui.amountLineEdit.text() == "":
            QMessageBox.warning(self, "", _translate("ItemViewDialog", "No amount was input"))
            return
        
        markup = self.item.getMarkup()
        
        for m in markup:
            if m["phase"] == self.getMarkup()["phase"] and self.markupEdit is None:
                QMessageBox.warning(self, "", _translate("ItemViewDialog", "Duplicate phase"))
                return
        
        if self.markupEdit is not None:
            markup.remove(self.markupEdit)
        markup.append(self.getMarkup())
        self.item.setMarkup(markup)
        self.accept()

class ItemCashOutNewDialog(QDialog):
    def __init__(self, item, cashOutEdit, parent=None):
        super(ItemCashOutNewDialog, self).__init__(parent)
        self.ui = Ui_ItemPhaseView()
        self.ui.setupUi(self)
        self.setWindowTitle(_translate("ItemPhaseView", "New Cash Out"))
        
        self.item = item
        
        self.ui.phaseSpinBox.setRange(1, item.period)
        self.ui.phaseSpinBox.valueChanged.connect(self.onPhaseChanged)
        self.onPhaseChanged(cashOutEdit)
        self.ui.amountLineEdit.setReadOnly(True)
        
        self.cashOutEdit = cashOutEdit
        self.loadCashOutEdit()
        self.ui.savePushButton.pressed.connect(self.onAccepted)
        self.ui.cancelPushButton.pressed.connect(self.reject)
    
    def onPhaseChanged(self, phase):
        if phase is None:
            phase = 1
        amount = self.item.getCashOutAmount(phase)
        self.ui.amountLineEdit.setText(str(amount))
    
    def loadCashOutEdit(self):
        if self.cashOutEdit is None:
            return
        
        self.ui.phaseSpinBox.setValue(self.cashOutEdit)
    
    def getCashOut(self):
        return self.ui.phaseSpinBox.value()
    
    def onAccepted(self):
        cashOut = self.item.getCashOut()
        
        if self.getCashOut() in cashOut and self.cashOutEdit is None:
            QMessageBox.warning(self, "", _translate("ItemViewDialog", "Duplicate phase"))
            return
        
        if self.cashOutEdit is not None:
            cashOut.remove(self.cashOutEdit)
        cashOut.append(self.getCashOut())
        self.item.setCashOut(cashOut)
        self.accept()

class TreeWidgetItem (QTreeWidgetItem):
    Category = Enum('Category', 'dualphase markup cashout')
    
    def __init__(self, category, data, strings):
        super(TreeWidgetItem, self).__init__(strings)
        self.category = category
        self.data = data
    
    def getCategory(self):
        return self.category
    
    def getData(self):
        return self.data

class ItemViewDialog(QDialog):
    def __init__(self, parent=None):
        super(ItemViewDialog, self).__init__(parent)
        self.ui = Ui_ItemView()
        self.ui.setupUi(self)
        self.ui.checkinLineEdit.setValidator(QIntValidator(self))
        self.ui.checkoutLineEdit.setValidator(QIntValidator(self))
        self.ui.feeLineEdit.setValidator(QIntValidator(self))
        self.ui.checkoutLineEdit.textEdited.connect(self.checkoutEdit)
        self.ui.feeCustomCheckBox.clicked.connect(self.customFee)
        self.ui.dualPhaseNewPushButton.pressed.connect(self.dualPhaseNew)
        self.ui.markupNewPushButton.pressed.connect(self.markupNew)
        self.ui.cashOutNewPushButton.pressed.connect(self.cashOutNew)
        
        self.ui.infoTreeWidget.setColumnCount(1)
        self.ui.infoTreeWidget.header().setVisible(False)
        self.ui.infoTreeWidget.itemDoubleClicked.connect(self.infoEdit)
        self.ui.infoTreeWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        editAction = QAction(_translate("ItemViewDialog", "Edit"), self.ui.infoTreeWidget)
        editAction.triggered.connect(self.infoContextMenuEditAction)
        self.ui.infoTreeWidget.addAction(editAction)
        deleteAction = QAction(_translate("ItemViewDialog", "Delete"), self.ui.infoTreeWidget)
        deleteAction.triggered.connect(self.infoContextMenuDeleteAction)
        self.ui.infoTreeWidget.addAction(deleteAction)
        
        self.ui.cancelPushButton.pressed.connect(self.onRejected)
        
        self.item = ItemModel()
    
    def checkoutEdit(self, text):
        if not self.ui.feeCustomCheckBox.isChecked():
            self.ui.feeLineEdit.setText(text)
    
    def customFee(self, checked):
        self.ui.feeLineEdit.setEnabled(checked)
        if not checked:
            self.ui.feeLineEdit.setText(self.ui.checkoutLineEdit.text())
    
    def dualPhaseNew(self, dualPhaseEdit=None):
        self.saveItem()
        dialog = ItemDualPhaseNewDialog(self.item, dualPhaseEdit, self)
        if dialog.exec() == QDialog.Accepted:
            self.loadInformation()
    
    def markupNew(self, markupEdit=None):
        self.saveItem()
        dialog = ItemMarkupNewDialog(self.item, markupEdit, self)
        if dialog.exec() == QDialog.Accepted:
            self.loadInformation()
    
    def cashOutNew(self, cashOutEdit=None):
        self.saveItem()
        if cashOutEdit is None and len(self.item.getCashOut()) > self.item.quantity:
            QMessageBox.warning(self, "", _translate("ItemViewDialog", "Exceed quantity"))
            return
        dialog = ItemCashOutNewDialog(self.item, cashOutEdit, self)
        if dialog.exec() == QDialog.Accepted:
            self.loadInformation()
    
    def infoEdit(self, item, column):
        category = item.getCategory()
        if category == TreeWidgetItem.Category.dualphase:
            self.dualPhaseNew(item.getData())
        elif category == TreeWidgetItem.Category.markup:
            self.markupNew(item.getData())
        else: # category == TreeWidgetItem.Category.cashout:
            self.cashOutNew(item.getData())
    
    def infoContextMenuEditAction(self):
        selectedItems = self.ui.infoTreeWidget.selectedItems()
        if len(selectedItems) > 0:
            self.infoEdit(selectedItems[0], 0)
    
    def infoContextMenuDeleteAction(self):
        selectedItems = self.ui.infoTreeWidget.selectedItems()
        if len(selectedItems) > 0:
            item = selectedItems[0]
            if QMessageBox.question(self, "", _translate("ItemViewDialog", "Continue to delete {}?").format(item.text(0))) == QMessageBox.Yes:
                category = item.getCategory()
                if category == TreeWidgetItem.Category.dualphase:
                    data = self.item.getDualPhase()
                    data.remove(item.getData())
                    self.item.setDualPhase(data)
                elif category == TreeWidgetItem.Category.markup:
                    data = self.item.getMarkup()
                    data.remove(item.getData())
                    self.item.setMarkup(data)
                else: # category == TreeWidgetItem.Category.cashout:
                    data = self.item.getCashOut()
                    data.remove(item.getData())
                    self.item.setCashOut(data)
                self.loadInformation()
    
    def onRejected(self):
        if session.dirty:
            session.rollback()
        self.reject()
    
    def loadInformation(self):
        self.ui.infoTreeWidget.clear()
        for dualPhase in self.item.getDualPhase():
            months = dualPhase["months"]
            if months == [1, 3, 5, 7, 9, 11]:
                months = _translate("ItemViewDialog", "odd")
            elif months == [2, 4, 6, 8, 10, 12]:
                months = _translate("ItemViewDialog", "even")
            elif months == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                months = _translate("ItemViewDialog", "every")
            item = TreeWidgetItem(TreeWidgetItem.Category.dualphase, dualPhase, \
                           [_translate("ItemViewDialog", "Since {}, {} month get dual phase").format(dualPhase["date"], months)])
            self.ui.infoTreeWidget.addTopLevelItem(item)
        
        for markup in self.item.getMarkup():
            item = TreeWidgetItem(TreeWidgetItem.Category.markup, markup, \
                                  [_translate("ItemViewDialog", "Since {} phase, rise in price {}").format(markup["phase"], markup["amount"])])
            self.ui.infoTreeWidget.addTopLevelItem(item)
        
        for cashOut in self.item.getCashOut():
            item = TreeWidgetItem(TreeWidgetItem.Category.cashout, cashOut, \
                                  [_translate("ItemViewDialog", "At {} phase, cash out {}").format(cashOut, self.item.getCashOutAmount(cashOut))])
            self.ui.infoTreeWidget.addTopLevelItem(item)
    
    def loadItem(self):
        self.ui.nameLineEdit.setText(self.item.name)
        self.ui.startDateEdit.setDate(self.item.startDate)
        self.ui.quantitySpinBox.setValue(self.item.quantity)
        self.ui.checkinLineEdit.setText(str(self.item.checkin))
        self.ui.checkoutLineEdit.setText(str(self.item.checkout))
        if self.item.fee is not None and self.item.fee != self.item.checkout:
            self.ui.feeCustomCheckBox.setChecked(True)
            self.customFee(True)
            self.ui.feeLineEdit.setText(str(self.item.fee))
        else:
            self.customFee(False)
        self.ui.periodSpinBox.setValue(self.item.period)
        self.loadInformation()
        self.ui.noteTextEdit.setPlainText(self.item.note)
    
    def saveItem(self):
        self.item.name = self.ui.nameLineEdit.text()
        self.item.startDate = qdate_to_date(self.ui.startDateEdit.date())
        self.item.quantity = self.ui.quantitySpinBox.value()
        self.item.checkin = int(self.ui.checkinLineEdit.text())
        self.item.checkout = int(self.ui.checkoutLineEdit.text())
        self.item.fee = None
        if self.ui.feeCustomCheckBox.isChecked():
            fee = self.ui.feeLineEdit.text()
            if fee != "" and int(fee) != self.item.checkout:
                self.item.fee = int(fee)
        self.item.period = self.ui.periodSpinBox.value()
        self.item.note = self.ui.noteTextEdit.toPlainText()

class ItemEditDialog(ItemViewDialog):
    def __init__(self, id, parent=None):
        super(ItemEditDialog, self).__init__(parent)
        self.ui.savePushButton.pressed.connect(self.onAccepted)
        
        self.item = session.query(ItemModel).filter_by(id = id).one()
        self.loadItem()
    
    def onAccepted(self):
        self.saveItem()
        session.commit()
        self.accept()

class ItemNewDialog(ItemViewDialog):
    def __init__(self, parent=None):
        super(ItemNewDialog, self).__init__(parent)
        self.ui.savePushButton.pressed.connect(self.onAccept)
    
    def onAccept(self):
        self.saveItem()
        session.add(self.item)
        session.commit()
        self.accept()