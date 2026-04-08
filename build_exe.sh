#!/bin/bash
# Build Strawberry Timer EXE using PyInstaller (Linux/Mac)

echo "========================================"
echo "  Strawberry Timer - Build Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed"
    exit 1
fi

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "[INFO] PyInstaller not found, installing..."
    pip3 install pyinstaller
fi

echo "[1/3] Cleaning previous build..."
rm -rf build dist

echo "[2/3] Building executable with PyInstaller..."
echo Using: python3 -m PyInstaller
python3 -m PyInstaller --clean pyqt_timer.spec

if [ $? -ne 0 ]; then
    echo "[ERROR] Build failed!"
    exit 1
fi

echo "[3/3] Build complete!"
echo ""
echo "========================================"
echo "  EXE Location: dist/StrawberryTimer"
echo "========================================"
echo ""

# Show dist directory
if [ -d "dist" ]; then
    ls -lh dist/
else
    echo "ERROR: dist directory not found"
    exit 1
fi
