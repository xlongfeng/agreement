pyrcc5.exe contract.qrc -o contract_rc.py
pyinstaller.exe -n 会子管理 -w -i images/contract.ico contract.pyw
asciidoctor README.adoc -o dist/会子管理/README.html
pause