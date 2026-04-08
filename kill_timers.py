#!/usr/bin/env python3
"""Kill all running Strawberry Timer processes."""

import psutil
import os
import signal
import sys
from pathlib import Path

def kill_strawberry_timers():
    """Kill all running Strawberry Timer processes."""
    print("🔍 Searching for running Strawberry Timer processes...")

    killed_count = 0
    current_pid = os.getpid()

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe']):
        try:
            # Get process info
            proc_info = proc.info

            # Skip the script itself
            if proc_info['pid'] == current_pid:
                continue

            # Check if this is a Python process
            if proc_info['name'] and 'python' in proc_info['name'].lower():
                cmdline = proc_info['cmdline'] or []
                exe = proc_info['exe'] or ''

                # Check if it's running any strawberry timer script
                is_timer_process = False
                if cmdline:
                    cmdline_str = ' '.join(cmdline).lower()
                    if 'strawberry' in cmdline_str or 'pyqt_timer' in cmdline_str or 'main.py' in cmdline_str:
                        # Check if it's from the StrawberryTimer directory
                        if 'stawberrytimer' in cmdline_str or 'strawberrytimer' in cmdline_str:
                            is_timer_process = True
                            print(f"  Found: PID {proc_info['pid']} - {' '.join(cmdline)}")

                # Also check exe path
                if exe and 'stawberrytimer' in exe.lower():
                    is_timer_process = True
                    print(f"  Found: PID {proc_info['pid']} - {exe}")

                if is_timer_process:
                    try:
                        proc.terminate()
                        print(f"  ✓ Terminated process PID {proc_info['pid']}")
                        killed_count += 1
                    except psutil.NoSuchProcess:
                        print(f"  ✗ Process {proc_info['pid']} already terminated")
                    except psutil.AccessDenied:
                        print(f"  ✗ Access denied to PID {proc_info['pid']} (try running as admin)")

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Also check for Tkinter window-based detection (less reliable)
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the temporary window

        # Try to detect and close any Toplevel windows with strawberry titles
        # Note: This is limited as we can only detect windows from our own process
        root.destroy()
    except:
        pass

    return killed_count

if __name__ == "__main__":
    killed = kill_strawberry_timers()

    if killed > 0:
        print(f"\n✅ Successfully closed {killed} Strawberry Timer instance(s)")
    else:
        print("\nℹ️ No Strawberry Timer instances found")

    print("\n💡 Tip: To prevent multiple instances, modify the code to use:")
    print("   - Single-instance enforcement (lock file or socket)")
    print("   - Check if another instance is running before starting")
