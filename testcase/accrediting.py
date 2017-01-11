#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date
from jinja2 import Environment, FileSystemLoader
from huizi import *

sampleItems = [
    {
        "name": "咪啊(山头尾顶)", # 会头
        "quantity": 2, # 名数
        "startdate": date(2010, 1, 9), # 开始时间
        "tip": 300, # 会头钱
        "checkin": 200, # 活期
        "checkout": 300, # 死期
        "periods": 122, # 期数
        "doubles": [ # 双期
            {
                "date": date(2011, 1, 1), # 生效时间
                "rule": [1, 3, 5, 7, 9, 11] # 规则
            },
            {
                "date": date(2013, 1, 1),
                "rule": [4, 8, 12]
            },
        ],
        "markups": [ # 涨价, 格式: dict(period, price)
            {"period": 40, "price": 10},
            {"period": 70, "price": 20}
        ],
        "cash": [ # 取现, 格式: 第几名
            60,
            80
        ],
        "notes": [# 备注
            "2009年十二月二十四日收会头钱",
            "2011年开始单月过双期"
        ]
    }
]

LEAP_MONTH = {
    2001: 4, 2004: 2, 2006: 7, 2009: 5, 2012: 4, 2014: 9, 2017: 6, 2020: 4,
    2023: 2, 2025: 6, 2028: 5, 2031: 3, 2033: 11, 2036: 6, 2039: 5, 2042: 2,
    2044: 7, 2047: 5, 2050: 3, 2052: 8, 2055: 6, 2058: 4, 2061: 3, 2063: 7,
    2066: 5, 2069: 4, 2071: 8, 2074: 6, 2077: 4, 2080: 3, 2082: 7, 2085: 5,
    2088: 4, 2090: 8, 2093: 6, 2096: 4, 2099: 2,
}

class Accrediting:
    def __init__(self, items):
        self.items = items
    
    def isDouble(self, month, year, doubles):
        index = -1
        for double in doubles:
            doubleDate = double["date"]
            if year >= doubleDate.year and month >= doubleDate.month:
                index = doubles.index(double)
        
        if index != -1:
            return month in doubles[index]["rule"]
        else:
            return False
    
    def adjustMonth(self, months, year, item):
        _months = []
        for month in months:
            _months.append("{}".format(month))
            if self.isDouble(month, year, item["doubles"]):
                _months.append("{}^双^".format(month))
            if LEAP_MONTH.get(year) == month:
                _months.append("{}^#闰#^".format(month))
        return _months
    
    def getAmount(self, period, index, item):
        amount = item["checkin"]
        
        for markup in item["markups"]:
            if period >= markup["period"]: # 涨价
                amount += markup["price"]
        
        if index < len(item["cash"]): # 已取现
            cachPeriod = item["cash"][index]
            if period >= cachPeriod:
                amount = item["checkout"]
        return amount
    
    def adoc(self):
        '''
        bill dict map:
        {
            name: name
            quantity: quantity
            cash: cash
            startdata: startdata
            tip: tip
            checkin: checkin
            checkout: checkout
            notes: notes
            details: [
                {
                    year: year
                    month: month
                    period: period list
                    amount: amount list
                    totalamount: totalamount
                    totalperiod: totalperiod
                }
            ]
        }
        '''
        bills = list()
        for item in self.items:
            quantity = item["quantity"]
            startdate = item["startdate"]
            checkin = item["checkin"]
            checkout = item["checkout"]
            periods = item["periods"]
            bill = dict(
                name = item["name"],
                quantity = quantity,
                cash = len(item["cash"]),
                startdate = startdate,
                tip = item["tip"],
                checkin = checkin,
                checkout = checkout,
                notes = item["notes"]
            )
            bill["details"] = list()
            period = 1
            for year in range(startdate.year, startdate.year + 15):
                startmonth = startdate.month if year == startdate.year else 1
                detail = dict()
                detail["year"] = year
                detail["month"] = []
                detail["period"] = []
                detail["amount"] = []
                detail["totalamount"] = 0
                
                months = range(startmonth, 13)
                months = self.adjustMonth(months, year, item)
                for month in months:
                    detail["month"].append(month)
                    detail["period"].append(period)
                    amount = 0
                    for index in range(0, quantity):
                        amount += self.getAmount(period, index, item)
                    detail["amount"].append(amount)
                    detail["totalamount"] += amount
                    period += 1
                    # 到达最后一期, 跳出循环
                    if period == periods:
                        break
                
                detail["totalperiod"] = len(detail["period"])
                bill["details"].append(detail)
                # 到达最后一期, 跳出循环
                if period == periods:
                    break
            
            bills.append(bill)
        
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('template.adoc')
        return template.render(bills = bills)

if __name__ == "__main__":
    accrediting = Accrediting(sampleItems)
    # accrediting = Accrediting(huizi)
    with open("accrediting.adoc", "w", encoding="utf8") as f:
        adoc = accrediting.adoc()
        # print(adoc)
        f.write(adoc)
