"""
Terminal-friendly GPSE runner with FINAL FIXES
Designed to run in PowerShell without context window issues
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Suppress unnecessary warnings
import warnings
warnings.filterwarnings("ignore")

if __name__ == "__main__":
    # Import and run the FINAL FIXED crew
    from main_crew import GPSECrewFixedFinal, logger, get_date_code
    
    try:
        print("\n" + "="*60)
        print("GPSE TERMINAL RUNNER - FINAL FIXED VERSION")
        print("="*60 + "\n")
        
        logger.info("Starting GPSE Final Fixed with terminal-friendly output...")
        gpse_crew = GPSECrewFixedFinal()
        
        # Create inputs with ALL required variables including date
        inputs = {
            "focus_areas": [
                "Ukraine-Russia conflict",
                "Middle East tensions",
                "US-China relations"
            ],
            "quality_threshold": 0.8,
            "time_window": "24 hours",
            # ADD THE MISSING DATE VARIABLES
            "date": datetime.now().strftime("%B %d, %Y"),  # e.g., "June 03, 2025"
            "current_date": datetime.now().strftime("%m%d%y"),  # e.g., "060325"
            "timestamp": datetime.now().isoformat(),
            "date_code": get_date_code(),
            "analysis_id": f"GGSM-{get_date_code()}-DailyAnalysis"
        }
        
        crew_instance = gpse_crew.crew()
        
        print(f"Date: {inputs['date']}")
        print(f"Analysis ID: {inputs['analysis_id']}")
        print("="*60 + "\n")
        
        logger.info("Executing crew with all fixes applied...")
        
        # Execute the crew
        result = crew_instance.kickoff(inputs=inputs)
        
        # Handle result logging carefully
        logger.info("Processing result...")
        
        # Verify file creation
        expected_file = Path(f"strategy_analyses/GGSM-{get_date_code()}-DailyAnalysis.md")
        
        print("\n" + "="*60)
        print("EXECUTION COMPLETE")
        print("="*60)
        
        if expected_file.exists():
            print(f"\n✓ SUCCESS: Analysis file created")
            print(f"  Location: {expected_file}")
            print(f"  Size: {expected_file.stat().st_size} bytes")
            
            # Show first few lines of the file
            with open(expected_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]
                print("\n  Preview:")
                print("  " + "-"*50)
                for line in lines:
                    print(f"  {line.rstrip()}")
                if len(lines) == 10:
                    print("  ...")
        else:
            print(f"\n✗ FAILURE: Expected file not found")
            print(f"  Expected: {expected_file}")
        
        print("\n" + "="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {str(e)}")
        logger.error(f"Critical error: {e}", exc_info=True)
        sys.exit(1)
