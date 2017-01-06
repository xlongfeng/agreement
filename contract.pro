QT += core gui widgets
TARGET = contract
TEMPLATE = app

SOURCES += \
    contract.pyw \
    item.py

FORMS += \
    contract.ui \
    itemview.ui \
    itemphaseview.ui \
    itemdualphasenewview.ui
	
TRANSLATIONS += contract_zh_CN.ts

RESOURCES += \
    contract.qrc