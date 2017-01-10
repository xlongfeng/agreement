call pyuic5.bat contract.ui -o ui_contract.py
call pyuic5.bat databaseview.ui -o ui_databaseview.py
call pyuic5.bat itemview.ui -o ui_itemview.py
call pyuic5.bat itemhistoryview.ui -o ui_itemhistoryview.py
call pyuic5.bat itemphaseview.ui -o ui_itemphaseview.py
call pyuic5.bat itemdualphasenewview.ui -o ui_itemdualphasenewview.py
pyrcc5.exe contract.qrc -o contract_rc.py
pylupdate5.exe contract.pro
pause