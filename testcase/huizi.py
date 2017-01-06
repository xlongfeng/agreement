#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date

huizi = [
    {
        "name": "咪啊(山头尾顶)",
        "quantity": 2,
        "startdate": date(2010, 1, 9),
        "tip": 300,
        "checkin": 200,
        "checkout": 300,
        "periods": 122,
        "doubles": [
            {
                "date": date(2011, 1, 1),
                "rule": [1, 3, 5, 7, 9, 11]
            },
        ],
        "markups": [
        ],
        "cash": [
            74,
            109
        ],
        "notes": [
            "2009年十二月二十四日收会头钱",
            "2011年开始单月过双期",
            "2014年四月二十四结算1名31200元"
        ]
    },
    
    {
        "name": "上管泉飞二子",
        "quantity": 3,
        "startdate": date(2010, 2, 26),
        "tip": 400,
        "checkin": 400,
        "checkout": 600,
        "periods": 64,
        "doubles": [
            {
                "date": date(2011, 1, 1),
                "rule": [3, 6, 9]
                },
            ],
        "markups": [
            {"period": 8, "price": 50}
            ],
        "cash": [
            42,
            55,
            56
            ],
        "notes": [
            "2010年正月二十六日收会头钱",
            "2010年九月起每名涨50元",
            "2011年开始3，6，9月过双期",
            "2012年11月底结算1名34350元",
            "2013年9月26结算1名36300元",
            "2013年10月26结算1名36450元"
        ]
    },
    
    {
        "name": "二兄",
        "quantity": 1,
        "startdate": date(2010, 5, 20),
        "tip": 400,
        "checkin": 400,
        "checkout": 600,
        "periods": 113,
        "doubles": [
            {
                "date": date(2012, 1, 1),
                "rule": [1, 3, 5, 7, 9, 11]
                },
            ],
        "markups": [
            ],
        "cash": [
            ],
        "notes": [
            "2010年四月二十日收会头钱",
            "2012年起单月过双期",
        ]
    }
]