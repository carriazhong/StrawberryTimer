@echo off
REM Quick build without icons - simpler and faster

echo ========================================
echo   Strawberry Timer - Quick Build
echo ========================================
echo.

REM Clean
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Building with PyInstaller (no icon)...
python -m PyInstaller --clean --noconfirm pyqt_timer.spec

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo.
    echo If you see icon errors, that's OK - EXE will still work.
    echo.
    if exist dist\StrawberryTimer.exe (
        echo SUCCESS: EXE created in dist folder
        echo.
        echo Press any key to test...
        pause >nul
        dist\StrawberryTimer.exe
    ) else (
        echo FAILURE: EXE not created
        pause
    )
    exit /b 1
)

echo.
echo ========================================
echo   Build Successful!
echo   EXE: dist\StrawberryTimer.exe
echo ========================================
echo.
echo Press any key to run the EXE...
pause >nul
dist\StrawberryTimer.exe
