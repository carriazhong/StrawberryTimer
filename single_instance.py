#!/usr/bin/env python3
"""Single instance manager for Strawberry Timer.

Prevents multiple instances from running simultaneously.
"""

import os
import sys
import socket
import errno
from pathlib import Path

class SingleInstance:
    """Ensures only one instance of the application runs."""

    def __init__(self, port=65432):
        """Initialize single instance checker.

        Args:
            port: Port number for socket lock.
        """
        self.port = port
        self.socket = None

    def __enter__(self):
        """Try to acquire lock."""
        try:
            # Try to create a socket and bind to localhost:port
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('127.0.0.1', self.port))
            # Keep socket open to maintain lock
            return True
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                # Port is already in use - another instance is running
                return False
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release lock."""
        if self.socket:
            self.socket.close()

def is_already_running(port=65432):
    """Check if another instance is already running.

    Args:
        port: Port number to check.

    Returns:
        True if another instance is running, False otherwise.
    """
    try:
        # Try to connect to the port
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.connect(('127.0.0.1', port))
        test_socket.close()
        return True  # Connection succeeded - instance is running
    except socket.error:
        return False  # Connection failed - no instance running


def run_single_instance(main_func, port=65432):
    """Run main function ensuring single instance.

    Args:
        main_func: Main application function to run.
        port: Port for instance lock.

    Returns:
        Return value from main_func, or None if another instance is running.
    """
    if is_already_running(port):
        print("⚠️ Strawberry Timer is already running!")
        print("   Only one instance is allowed at a time.")
        print("   Check the desktop for the floating timer widget.")
        return None

    with SingleInstance(port):
        try:
            return main_func()
        except KeyboardInterrupt:
            print("\n👋 Timer stopped by user")
            return None


if __name__ == "__main__":
    # Test the single instance checker
    if is_already_running():
        print("✗ Another instance is already running")
    else:
        print("✓ No other instance detected")
        print("  You can now start a new instance")
