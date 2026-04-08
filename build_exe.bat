@echo off
REM Build Strawberry Timer EXE using PyInstaller

echo ========================================
echo   Strawberry Timer - Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [INFO] PyInstaller not found, installing...
    pip install pyinstaller
)

echo.
echo [1/3] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [2/3] Building executable with PyInstaller...
echo Using: python -m PyInstaller
python -m PyInstaller --clean pyqt_timer.spec

if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo [3/3] Build complete!
echo.
echo ========================================
echo   EXE Location: dist\StrawberryTimer.exe
echo ========================================
echo.
if exist dist\StrawberryTimer.exe (
    echo Press any key to open output folder...
    pause >nul
    explorer dist
) else (
    echo EXE not found in dist folder. Check for errors above.
    pause
)
