"""
GPSE Deep Dive Analysis Launcher
Executes the enhanced GPSE system that produces both executive brief and regional deep dives
"""

import subprocess
import sys
import os
from datetime import datetime

def main():
    """Launch the GPSE Deep Dive Analysis"""
    print("\n" + "="*60)
    print("GPSE DEEP DIVE ANALYSIS LAUNCHER")
    print("="*60)
    print("\nThis will generate:")
    print("1. Executive Brief (1-2 pages)")
    print("2. Regional Deep Dives (5-10 pages each):")
    print("   - Americas (North and South)")
    print("   - Europe and Russia")
    print("   - Middle East and North Africa")
    print("   - Sub-Saharan Africa")
    print("   - South and Central Asia")
    print("   - East Asia and Pacific")
    print("   - Global Threats and Non-State Actors")
    print("3. Analysis Index linking all documents")
    print("\nEstimated processing time: 10-20 minutes")
    print("="*60)
    
    # Check for API keys
    api_keys_present = True
    missing_keys = []
    
    if not os.getenv("OPENAI_API_KEY"):
        missing_keys.append("OPENAI_API_KEY")
        api_keys_present = False
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        missing_keys.append("ANTHROPIC_API_KEY")
        api_keys_present = False
    
    if not api_keys_present:
        print("\n⚠️  WARNING: Missing API keys:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\nPlease set these in your .env file or environment variables.")
        return
    
    # Confirm execution
    response = input("\nProceed with deep dive analysis? (y/n): ")
    if response.lower() != 'y':
        print("Analysis cancelled.")
        return
    
    print("\nStarting GPSE Deep Dive Analysis...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run the deep dive analysis
        result = subprocess.run(
            [sys.executable, "main_crew_global_deep_dive.py"],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ Deep Dive Analysis completed successfully!")
            print("\nCheck the strategy_analyses/ directory for:")
            print("- Executive Brief")
            print("- Regional Deep Dive files")
            print("- Analysis Index")
        else:
            print("\n❌ Analysis failed. Check the error messages above.")
            
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error launching analysis: {str(e)}")

if __name__ == "__main__":
    main()
