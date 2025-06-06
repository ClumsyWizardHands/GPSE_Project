"""
Simple test to check if main_crew.py can start without errors
"""

import subprocess
import sys
import time

print("Testing if main_crew.py can start without immediate errors...")

# Start the process
proc = subprocess.Popen(
    [sys.executable, 'main_crew.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding='utf-8',
    errors='replace'
)

# Wait a bit to see if there are immediate errors
print("Waiting 3 seconds to check for immediate errors...")
time.sleep(3)

# Check if process crashed immediately
if proc.poll() is not None:
    # Process ended already (likely an error)
    stdout, stderr = proc.communicate()
    print(f"\nProcess ended with return code: {proc.returncode}")
    if stderr:
        print(f"\nSTDERR:\n{stderr}")
    if stdout:
        print(f"\nSTDOUT:\n{stdout}")
else:
    # Process is still running (good sign)
    print("\nGood! Process is still running after 3 seconds.")
    print("This means no immediate syntax/import errors.")
    print("Terminating the test process...")
    proc.terminate()
    print("Test completed successfully!")
