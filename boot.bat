@echo off

cd D:\SUMI
call D:\SUMI\env\Scripts\activate.bat

python mange.py runserver 192.168.5.202:9000

cmd /k