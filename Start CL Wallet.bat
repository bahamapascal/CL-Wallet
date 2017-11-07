@echo off
if not "%1" == "max" start /MAX cmd /c %0 max & exit/b
mode con: cols=140 lines=2000
python Wallet.py
pause
