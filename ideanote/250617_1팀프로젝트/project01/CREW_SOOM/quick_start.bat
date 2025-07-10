@echo off
chcp 65001 > nul
title CREW_SOOM 침수 예측 AI 시스템

:menu
cls
echo.
echo  
echo                                        
echo       CREW_SOOM 침수 예측 AI 시스템     
echo  
echo  
echo.
echo  원하는 작업을 선택하세요:
echo.
echo  1.  시스템 설치
echo  2.  시스템 체크
echo  3.  시스템 실행
echo  4.  README 보기
echo  5.  종료
echo.
set /p choice=선택 (1-5): 

if "%choice%"=="1" goto install
if "%choice%"=="2" goto check
if "%choice%"=="3" goto run
if "%choice%"=="4" goto readme
if "%choice%"=="5" goto exit

echo 잘못된 선택입니다. 다시 선택하세요.
pause
goto menu

:install
echo.
echo  시스템 설치 중...
python setup.py
echo.
echo 설치가 완료되었습니다!
pause
goto menu

:check
echo.
echo  시스템 체크 중...
python check_system.py
echo.
pause
goto menu

:run
echo.
echo  시스템 실행 중...
echo 웹 브라우저에서 http://localhost:5000 으로 접속하세요
echo 로그인: admin / 1234
echo.
python run.py
pause
goto menu

:readme
echo.
echo 📝 README 파일 내용:
echo.
type README.md
echo.
pause
goto menu

:exit
echo.
echo  CREW_SOOM을 이용해주셔서 감사합니다!
echo.
exit