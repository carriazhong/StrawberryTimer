#!/bin/bash
# Quick build without icons - Linux/Mac

echo "========================================"
echo "  Strawberry Timer - Quick Build"
echo "========================================"
echo ""

# Clean
rm -rf build dist

echo "Building with PyInstaller (no icon)..."
python3 -m PyInstaller --clean --noconfirm pyqt_timer.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Build failed!"
    echo ""
    echo "If you see icon errors, that's OK - EXE will still work."
    echo ""
    if [ -f "dist/StrawberryTimer" ]; then
        echo "SUCCESS: EXE created in dist folder"
        echo ""
        read -p "Press Enter to test... "
        "./dist/StrawberryTimer"
    else
        echo "FAILURE: EXE not created"
    fi
    exit 1
fi

echo ""
echo "========================================"
echo "  Build Successful!"
echo "  EXE: dist/StrawberryTimer"
echo "========================================"
echo ""

if [ -f "dist/StrawberryTimer" ]; then
    read -p "Press Enter to run the EXE... "
    "./dist/StrawberryTimer"
fi
