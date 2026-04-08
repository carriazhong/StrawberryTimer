@echo off
REM Simple build script for Strawberry Timer EXE
REM Uses python -m to avoid PATH issues

echo Building Strawberry Timer EXE...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build using python -m PyInstaller (works even if pyinstaller not in PATH)
python -m PyInstaller --clean pyqt_timer.spec

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo Check the error messages above.
    echo.
    echo Common issues:
    echo 1. PyQt5 not installed: pip install PyQt5
    echo 2. PyInstaller not installed: pip install pyinstaller
    echo 3. Missing files: Check that pyqt_timer.py exists
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Build Successful!
echo   EXE Location: dist\StrawberryTimer.exe
echo ========================================
echo.

if exist dist\StrawberryTimer.exe (
    echo Press any key to open dist folder...
    pause >nul
    explorer dist
) else (
    echo WARNING: EXE not found in dist folder
    echo Check for errors above.
    pause
)
