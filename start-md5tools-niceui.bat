@echo off
cd /d "%~dp0"
call .env\Scripts\activate.bat
python md5-tools-niceui.py
pause