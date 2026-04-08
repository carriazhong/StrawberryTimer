#!/bin/bash
# Kill all Strawberry Timer processes

echo "Searching for Strawberry Timer processes..."

# Try to kill Python processes using taskkill
taskkill //F //IM python.exe 2>/dev/null
taskkill //F //IM pythonw.exe 2>/dev/null

echo ""
echo "✓ Attempted to kill all Python processes"
echo ""
echo "If timers are still visible, please:"
echo "1. Press Ctrl+Shift+Esc to open Task Manager"
echo "2. Find and End Task all python.exe or pythonw.exe processes"
echo "3. Or run: cmd /c taskkill //F //IM python.exe"
