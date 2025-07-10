@echo off
chcp 65001 > nul
echo  시스템 환경 체크
echo ==================
echo.
python check_system.py
echo.
pause