call pyuic5.bat agreement.ui -o ui_agreement.py
call pyuic5.bat itemview.ui -o ui_itemview.py
call pyuic5.bat itemphaseview.ui -o ui_itemphaseview.py
call pyuic5.bat itemdualphaseview.ui -o ui_itemdualphaseview.py
pyrcc5.exe agreement.qrc -o agreement_rc.py
pylupdate5.exe agreement.pro
pause