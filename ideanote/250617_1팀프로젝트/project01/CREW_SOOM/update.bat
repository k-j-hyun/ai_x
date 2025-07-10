@echo off
chcp 65001 > nul
echo  시스템 업데이트
echo ================
echo.
echo 패키지 업데이트 중...
pip install --upgrade -r requirements.txt
echo.
echo 업데이트가 완료되었습니다!
pause