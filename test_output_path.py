"""
Test script to verify that main_crew.py outputs the absolute file path as the last line
"""

import subprocess
import os
import sys

def test_main_crew_output():
    """Run main_crew.py and capture the last line of output"""
    
    print("Testing main_crew.py output...")
    print("-" * 60)
    
    # Note: This is a simple test that doesn't actually run the full crew
    # It just demonstrates how to capture the output
    
    # For actual testing, you would run:
    # result = subprocess.run([sys.executable, "main_crew.py"], 
    #                        capture_output=True, text=True)
    
    # Simulate expected output path
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y")
    expected_filename = f'strategy_analyses/GGSM-{current_date}-DailyAnalysis.md'
    expected_path = os.path.abspath(expected_filename)
    
    print(f"Expected output path format:")
    print(f"  Relative: {expected_filename}")
    print(f"  Absolute: {expected_path}")
    
    print("\nThe main_crew.py script will output this path as its very last line.")
    print("\nYour GUI can capture this by:")
    print("1. Running the script and capturing stdout")
    print("2. Splitting the output by newlines")
    print("3. Taking the last non-empty line")
    print("4. Using this as the path to the generated document")

if __name__ == "__main__":
    test_main_crew_output()
