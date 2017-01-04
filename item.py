#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
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
                             QWidget, QGroupBox, QMessageBox)
from PyQt5.QtGui import QIntValidator

from ui_itemview import *
from ui_itemphaseview import *
from ui_itemdualphaseview import *

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

engine = create_engine('sqlite:///storage.sqlite')
Base.metadata.create_all(engine)

session = sessionmaker(engine)()

class ItemDualPhaseView(QGroupBox):
    def __init__(self, index, parent=None):
        super(ItemDualPhaseView, self).__init__(parent)
        self.ui = Ui_ItemDualPhaseView()
        self.ui.setupUi(self)
        self.setTitle(_translate("ItemDualPhaseView", "Rule {}").format(index + 1))
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
    
    def loadDualPhase(self, phase):
        self.setChecked(True)
        self.ui.dateEdit.setDate(QDate.fromString(phase["date"], Qt.ISODate))
        for i in range(0, 12):
            if (i + 1) in phase["months"]:
                self.monthCheckBox[i].setChecked(True)
    
    def monthHasChecked(self):
        hasChecked = False
        for checkBox in self.monthCheckBox:
            if checkBox.isChecked():
                hasChecked = True
                break;
        return hasChecked
    
    def dualPhase(self):
        months = list()
        for i in range(0, 12):
            if self.monthCheckBox[i].isChecked():
                months.append(i + 1)
        return dict(date=qdate_to_date(self.ui.dateEdit.date()).isoformat(),
                    months=months)

class ItemDualPhaseEditDialog(QDialog):
    def __init__(self, dualPhase, parent=None):
        super(ItemDualPhaseEditDialog, self).__init__(parent)
        self.rules = list()
        vLayout = QVBoxLayout(self)
        
        rule = ItemDualPhaseView(0, self)
        self.rules.append(rule)
        vLayout.addWidget(rule)
        
        rule = ItemDualPhaseView(1, self)
        self.rules.append(rule)
        vLayout.addWidget(rule)
        
        rule = ItemDualPhaseView(2, self)
        self.rules.append(rule)
        vLayout.addWidget(rule)
        
        rule = ItemDualPhaseView(3, self)
        self.rules.append(rule)
        vLayout.addWidget(rule)
        
        self.dialogButtonBox = QDialogButtonBox(self)
        self.dialogButtonBox.addButton(_translate("ItemViewDialog", "Save"), QDialogButtonBox.AcceptRole)
        self.dialogButtonBox.addButton(_translate("ItemViewDialog", "Cancel"), QDialogButtonBox.RejectRole)
        self.dialogButtonBox.accepted.connect(self.accept)
        self.dialogButtonBox.rejected.connect(self.reject)
        vLayout.addWidget(self.dialogButtonBox)
        
        self.loadDualPhase(dualPhase)
    
    def loadDualPhase(self, dualPhase):
        index = 0
        for phase in dualPhase:
            rule = self.rules[index]
            rule.loadDualPhase(phase)
            index += 1
    
    def dualPhase(self):
        dualPhaseRule = list()
        for rule in self.rules:
            if rule.isChecked() and rule.monthHasChecked():
                dualPhaseRule.append(rule.dualPhase())
        return dualPhaseRule

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
        self.ui.dualPhaseEditPushButton.pressed.connect(self.dualPhaseEdit)
        
        self.item = ItemModel()
    
    def checkoutEdit(self, text):
        if not self.ui.feeCustomCheckBox.isChecked():
            self.ui.feeLineEdit.setText(text)
    
    def customFee(self, checked):
        self.ui.feeLineEdit.setEnabled(checked)
        if not checked:
            self.ui.feeLineEdit.setText(self.ui.checkoutLineEdit.text())
    
    def dualPhaseEdit(self):
        dualPhase = self.loadDualPhase()
        dialog = ItemDualPhaseEditDialog(dualPhase, self)
        if dialog.exec() == QDialog.Accepted:
            dualPhase = dialog.dualPhase()
            self.item.dualPhase = json.dumps(dualPhase)
            self.ui.infoTextEdit.setPlainText(self.loadInformation())
    
    def loadDualPhase(self):
        if self.item.dualPhase is not None and self.item.dualPhase != "":
            dualPhase = json.loads(self.item.dualPhase)
        else:
            dualPhase = []
        return dualPhase
    
    def loadInformation(self):
        dualPhase = self.loadDualPhase()
        info = ""
        for phase in dualPhase:
            months = phase["months"]
            if months == [1, 3, 5, 7, 9, 11]:
                months = _translate("ItemViewDialog", "odd")
            elif months == [2, 4, 6, 8, 10, 12]:
                months = _translate("ItemViewDialog", "even")
            elif months == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                months = _translate("ItemViewDialog", "every")
            info += _translate("ItemViewDialog", "Since {}, {} month get dual phase\n").format(phase["date"], months)
        return info
    
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
        self.ui.infoTextEdit.setPlainText(self.loadInformation())
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
        self.ui.dialogButtonBox = QDialogButtonBox(self)
        self.ui.dialogButtonBox.addButton(_translate("ItemViewDialog", "Save"), QDialogButtonBox.AcceptRole)
        self.ui.dialogButtonBox.addButton(_translate("ItemViewDialog", "Cancel"), QDialogButtonBox.RejectRole)
        self.layout().addWidget(self.ui.dialogButtonBox)
        self.ui.dialogButtonBox.accepted.connect(self.save)
        self.ui.dialogButtonBox.rejected.connect(self.reject)
        
        self.item = session.query(ItemModel).filter_by(id = id).one()
        self.loadItem()
    
    def save(self):
        self.saveItem()
        session.commit()
        self.accept()

class ItemNewDialog(ItemViewDialog):
    def __init__(self, parent=None):
        super(ItemNewDialog, self).__init__(parent)
        self.ui.dialogButtonBox = QDialogButtonBox(self)
        self.ui.dialogButtonBox.addButton(_translate("ItemViewDialog", "New"), QDialogButtonBox.AcceptRole)
        self.ui.dialogButtonBox.addButton(_translate("ItemViewDialog", "Cancel"), QDialogButtonBox.RejectRole)
        self.layout().addWidget(self.ui.dialogButtonBox)
        self.ui.dialogButtonBox.accepted.connect(self.new)
        self.ui.dialogButtonBox.rejected.connect(self.reject)
    
    def new(self):
        self.saveItem()
        session.add(self.item)
        session.commit()
        self.accept()