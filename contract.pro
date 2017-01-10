QT += core gui widgets
TARGET = contract
TEMPLATE = app

SOURCES += \
    contract.pyw \
    database.py \
    item.py

FORMS += \
    contract.ui \
    databaseview.ui \
    itemview.ui \
    itemhistoryview.ui \
    itemphaseview.ui \
    itemdualphasenewview.ui
	
TRANSLATIONS += contract_zh_CN.ts

RESOURCES += \
    contract.qrc