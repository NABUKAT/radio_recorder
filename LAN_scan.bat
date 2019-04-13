@echo off

setlocal enabledelayedexpansion
for /f "tokens=1,2* usebackq delims=^:" %%i in (`ipconfig ^| findstr /n /r "." ^| findstr /r "IPv4 アドレス"`) DO @set IP=%%k
for /f "tokens=1,2,3 usebackq delims=^." %%i in (`echo %IP%`) DO @set nw=%%i.%%j.%%k
echo Raspberry Piを探索中です。
echo しばらくお待ち下さい。数分かかる場合があります。
for /l %%i in (0,1,255) do ping -w 1 -n 1 %nw%.%%i >nul && arp -a %nw%.%%i >nul
for /f "tokens=1,2 usebackq delims= " %%i in (`arp -a ^| find "b8-27-eb"`) DO @set IP=%%i
echo.
echo Raspberry PiのIPアドレス： %IP%
echo.

pause
