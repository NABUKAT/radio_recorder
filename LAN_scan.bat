@echo off

setlocal enabledelayedexpansion
for /f "tokens=1,2* usebackq delims=^:" %%i in (`ipconfig ^| findstr /n /r "." ^| findstr /r "IPv4 �A�h���X"`) DO @set IP=%%k
for /f "tokens=1,2,3 usebackq delims=^." %%i in (`echo %IP%`) DO @set nw=%%i.%%j.%%k
echo Raspberry Pi��T�����ł��B
echo ���΂炭���҂��������B����������ꍇ������܂��B
for /l %%i in (0,1,255) do ping -w 1 -n 1 %nw%.%%i >nul && arp -a %nw%.%%i >nul
for /f "tokens=1,2 usebackq delims= " %%i in (`arp -a ^| find "b8-27-eb"`) DO @set IP=%%i
echo.
echo Raspberry Pi��IP�A�h���X�F %IP%
echo.

pause
