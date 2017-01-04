QT += core gui widgets
TARGET = agreement
TEMPLATE = app

SOURCES += \
    agreement.pyw \
    item.py

FORMS += \
    agreement.ui \
    itemview.ui \
    itemphaseview.ui \
    itemdualphaseview.ui
	
TRANSLATIONS += agreement_zh_CN.ts

RESOURCES += \
    agreement.qrc