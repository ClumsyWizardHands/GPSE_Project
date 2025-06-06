"""
Debug script to test subprocess execution of main_crew.py
"""

import subprocess
import sys
import os

print(f"Current working directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")
print(f"main_crew.py exists: {os.path.exists('main_crew.py')}")

print("\nTrying to run main_crew.py...")

try:
    result = subprocess.run(
        [sys.executable, 'main_crew.py'],
        capture_output=True,
        text=True,
        timeout=10  # 10 second timeout for testing
    )
    
    print(f"\nReturn code: {result.returncode}")
    print(f"\nSTDOUT length: {len(result.stdout)} characters")
    print(f"STDERR length: {len(result.stderr)} characters")
    
    if result.stderr:
        print(f"\nSTDERR (first 500 chars):\n{result.stderr[:500]}")
    
    if result.returncode != 0:
        print("\nProcess failed!")
    else:
        print("\nProcess succeeded!")
        # Try to get the last line
        lines = result.stdout.strip().split('\n')
        if lines:
            print(f"Last line of output: {lines[-1]}")
            
except subprocess.TimeoutExpired:
    print("\nError: Process timed out after 10 seconds")
except Exception as e:
    print(f"\nError: {type(e).__name__}: {str(e)}")
