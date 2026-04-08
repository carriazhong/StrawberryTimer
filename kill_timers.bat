@echo off
REM Kill all Strawberry Timer processes

echo Searching for Strawberry Timer processes...

REM Kill Python processes running strawberry timer
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *Strawberry*" 2>nul
taskkill /F /FI "IMAGENAME eq pythonw.exe" /FI "WINDOWTITLE eq *Strawberry*" 2>nul

REM Kill any Python processes in StrawberryTimer directory
taskkill /F /IM python.exe /FI "MODULES eq *StawberryTimer*" 2>nul
taskkill /F /IM pythonw.exe /FI "MODULES eq *StawberryTimer*" 2>nul

echo.
echo If timers are still visible, you can:
echo 1. Run: taskkill /F /IM python.exe
echo 2. Or run: kill_timers.py
echo 3. Or manually close them from Task Manager
echo.
pause
