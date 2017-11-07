@echo off
if not "%1" == "max" start /MAX cmd /c %0 max & exit/b
mode con: cols=140 lines=2000
C:\Users\Pascal\AppData\Local\Programs\Python\Python36\python Wallet.py
pause
