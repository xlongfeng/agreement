#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
import sys
import math
from datetime import datetime, date
from jinja2 import Environment, BaseLoader, FileSystemLoader, TemplateNotFound
from sqlalchemy import desc

from PyQt5.QtCore import QIODevice, QFile

from database import *
from item import ItemModel

LEAP_MONTH = {
    2001: 4, 2004: 2, 2006: 7, 2009: 5, 2012: 4, 2014: 9, 2017: 6, 2020: 4,
    2023: 2, 2025: 6, 2028: 5, 2031: 3, 2033: 11, 2036: 6, 2039: 5, 2042: 2,
    2044: 7, 2047: 5, 2050: 3, 2052: 8, 2055: 6, 2058: 4, 2061: 3, 2063: 7,
    2066: 5, 2069: 4, 2071: 8, 2074: 6, 2077: 4, 2080: 3, 2082: 7, 2085: 5,
    2088: 4, 2090: 8, 2093: 6, 2096: 4, 2099: 2,
}

class QFileLoader(BaseLoader):
    def __init__(self, path):
        self.path = path
    
    def get_source(self, environment, template):
        filename = path.join(self.path, template)
        file = QFile(filename)
        if not file.exists():
            raise TemplateNotFound(template)
        file.open(QIODevice.ReadOnly)
        source = file.readAll().data().decode('utf-8')
        return source, filename, lambda: True

class Accrediting:
    def __init__(self, id=None):
        self.id = id
        session = Database.instance().session()
        if id is not None:
            self.item = session.query(ItemModel).filter_by(id = id).one()
        else:
            self.items =  session.query(ItemModel).order_by(desc(ItemModel.startDate))
    
    def isDouble(self, month, year, doubles):
        index = -1
        for double in doubles:
            doubleDate = datetime.strptime(double["date"], "%Y-%m-%d").date()
            if year >= doubleDate.year and month >= doubleDate.month:
                index = doubles.index(double)
        
        if index != -1:
            return month in doubles[index]["months"]
        else:
            return False
    
    def adjustMonth(self, months, year, item):
        _months = []
        for month in months:
            _months.append(dict(month=month, type=0))
            if self.isDouble(month, year, item.getDualPhase()):
                _months.append(dict(month=month, type=1)) # 双
            if LEAP_MONTH.get(year) == month:
                _months.append(dict(month=month, type=2)) # 闰
        return _months
    
    def getAmount(self, phase, index, item):
        amount = item.checkin
        
        for markup in item.getMarkup():
            if phase >= markup["phase"]: # 涨价
                amount += markup["amount"]
        
        cashOut = item.getCashOut()
        if index < len(cashOut): # 已取现
            cachPhase = cashOut[index]
            if phase >= cachPhase:
                amount = item.checkout
        return amount
    
    def toSummaryHtml(self):
        '''
        bill:
        {
            year: year
            totalamount: totalamount
            details: [
                dict(
                    name = name,
                    checking = checking,
                    quantity = quantity,
                    period = period,
                    unfinished = unfinished,
                    finished = finished,
                    totalamount = totalamount,
                    yearamount = yearamount,
                    percent = percent
                )
            ]
        }
        first stage
        bills: {
            year: [bill]
        }
        billList: [
            bill
        ]
        '''
        bills = dict()
        for item in self.items:
            quantity = item.quantity
            startdate = item.startDate
            checkin = item.checkin
            checkout = item.checkout
            period = item.period
            fee = item.fee if item.fee is not None else checkout
            phase = 1
            totalamount = 0
            for year in range(startdate.year, startdate.year + 15):
                startmonth = startdate.month if year == startdate.year else 1
                yearperiod = 0
                yearamount = 0
                
                months = range(startmonth, 13)
                months = self.adjustMonth(months, year, item)
                for month in months:
                    amount = 0
                    for index in range(0, quantity):
                        amount += self.getAmount(phase, index, item)
                    yearperiod += 1
                    yearamount += amount
                    phase += 1
                    # 到达最后一期, 最后一期不需要供, 跳出循环
                    if phase == period:
                        break
                # 计算完成一年
                totalamount += yearamount
                # print(year, period - phase, phase, yearamount, totalamount)
                bill = bills.get(year, dict(year=year, totalamount=0, details=[]))
                bill["totalamount"] += yearamount
                bill["details"].append(dict(
                    name = item.name,
                    startdate = item.startDatetoString(),
                    checking = 0,
                    quantity = quantity,
                    period = period,
                    unfinished = period - phase,
                    finished = phase,
                    totalamount = totalamount,
                    yearperiod = yearperiod,
                    yearamount = yearamount,
                    percent = math.ceil(phase * 100 / period)
                ))
                bills[year] = bill
                # 到达最后一期, 跳出循环
                if phase == period:
                    break
        
        # reorder
        billList = []
        for year in sorted(bills.keys(), reverse=True):
            if year > date.today().year + 1:
                continue
            billList.append(bills[year])
        
        if "sep-rc" in sys.argv:
            env = Environment(loader=FileSystemLoader('templates'))
        else:
            env = Environment(loader=QFileLoader(':/templates'))
        template = env.get_template('summary.html')
        return template.render(name=Database.instance().name(), date=datetime.today().strftime("%Y-%m-%d %H:%M:%S"), bills=billList)
    
    def toItemHtml(self):
        '''
        bill dict map:
        {    
            name: name
            startdata: startdata
            checking: checking
            quantity: quantity
            period: period
            fee: fee
            checkin: checkin
            checkout: checkout
            notes: notes
            details: [
                {
                    year: year
                    month: month
                    period: period list
                    amount: amount list
                    yearamount: yearamount
                    yearperiod: yearperiod
                    finished: finished
                    totalamount: totalamount
                    percent: percent
                }
            ]
        }
        '''
        item = self.item
        quantity = item.quantity
        startdate = item.startDate
        cashOut = len(item.getCashOut())
        checkin = item.checkin
        checkout = item.checkout
        period = item.period
        fee = item.fee if item.fee is not None else checkout
        bill = dict(
            name = item.name,
            startdate = item.startDatetoString(),
            checking = quantity - cashOut,
            quantity = quantity,
            period = period,
            fee = fee,
            checkin = checkin,
            checkout = checkout,
            note = item.note
        )
        bill["details"] = list()
        phase = 1
        totalamount = 0
        for year in range(startdate.year, startdate.year + 15):
            startmonth = startdate.month if year == startdate.year else 1
            detail = dict()
            detail["year"] = year
            detail["month"] = []
            detail["phase"] = []
            detail["amount"] = []
            detail["yearamount"] = 0
            
            months = range(startmonth, 13)
            months = self.adjustMonth(months, year, item)
            for month in months:
                detail["month"].append(month)
                phaseType = dict(phase=phase, markup=False, cashout=False)
                for markup in item.getMarkup():
                    if markup["phase"] == phase:
                        phaseType["markup"] = True
                        break
                if phase in item.getCashOut():
                    phaseType["cashout"] = True
                detail["phase"].append(phaseType)
                amount = 0
                for index in range(0, quantity):
                    amount += self.getAmount(phase, index, item)
                detail["amount"].append(amount)
                detail["yearamount"] += amount
                phase += 1
                # 到达最后一期, 最后一期不需要供, 跳出循环
                if phase == period:
                    break
            # 计算完成一年
            totalamount += detail["yearamount"]
            detail["yearperiod"] = len(detail["phase"])
            detail["finished"] = phase
            detail["totalamount"] = totalamount
            detail["percent"] = math.ceil(phase * 100 / period)
            bill["details"].append(detail)
            # 到达最后一期, 跳出循环
            if phase == period:
                break
        if "sep-rc" in sys.argv:
            env = Environment(loader=FileSystemLoader('templates'))
        else:
            env = Environment(loader=QFileLoader(':/templates'))
        template = env.get_template('item.html')
        return template.render(bill = bill)