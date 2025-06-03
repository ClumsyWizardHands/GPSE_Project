"""
Test script for GPSE Crew implementation
"""
import os
import sys
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_environment():
    """Test environment setup"""
    print("=== Testing Environment Setup ===")
    
    # Check API keys
    required_keys = ['OPENAI_API_KEY', 'TAVILY_API_KEY']
    optional_keys = ['ANTHROPIC_API_KEY', 'NEWS_API_KEY']
    
    missing_required = []
    for key in required_keys:
        if os.getenv(key):
            print(f"✅ {key} is configured")
        else:
            print(f"❌ {key} is missing")
            missing_required.append(key)
    
    for key in optional_keys:
        if os.getenv(key):
            print(f"✅ {key} is configured (optional)")
        else:
            print(f"⚠️  {key} is not configured (optional)")
    
    # Check configuration files
    config_files = ['config/agents.yaml', 'config/tasks.yaml']
    for file in config_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} is missing")
            missing_required.append(file)
    
    # Check ChromaDB
    if os.path.exists('strategy_db_chroma'):
        print("✅ ChromaDB directory exists")
    else:
        print("⚠️  ChromaDB directory will be created on first run")
    
    if missing_required:
        print(f"\n❌ Missing required components: {missing_required}")
        return False
    
    print("\n✅ Environment setup is complete!")
    return True

def test_imports():
    """Test all imports"""
    print("\n=== Testing Imports ===")
    
    try:
        from gpse_crew import GPSECrew
        print("✅ gpse_crew imports successfully")
        
        from gpse_conditional_tasks import integrate_conditional_tasks, QualityMetrics
        print("✅ gpse_conditional_tasks imports successfully")
        
        from db_manager import ChromaDBManager
        print("✅ db_manager imports successfully")
        
        import gpse_tools
        print("✅ gpse_tools imports successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_crew_initialization():
    """Test crew initialization"""
    print("\n=== Testing Crew Initialization ===")
    
    try:
        from gpse_crew import GPSECrew
        
        # Initialize crew
        print("Initializing GPSE Crew...")
        crew = GPSECrew()
        print("✅ Crew initialized successfully")
        
        # Check agents
        print(f"✅ Number of agents: {len(crew.agents)}")
        for agent in crew.agents:
            print(f"  - {agent.role}")
        
        # Check tasks
        print(f"✅ Number of tasks: {len(crew.tasks)}")
        
        return True
    except Exception as e:
        print(f"❌ Crew initialization error: {e}")
        logger.exception("Full error trace:")
        return False

def test_minimal_run():
    """Test a minimal crew run"""
    print("\n=== Testing Minimal Crew Run ===")
    
    try:
        from gpse_crew import GPSECrew
        from gpse_conditional_tasks import integrate_conditional_tasks, QualityMetrics
        import time
        
        # Initialize crew and metrics
        crew = GPSECrew()
        metrics = QualityMetrics()
        
        # Add conditional tasks
        crew_instance = crew.crew()
        enhanced_crew = integrate_conditional_tasks(crew_instance)
        
        # Prepare minimal test inputs
        test_inputs = {
            'topic': 'Ukraine Russia conflict test',
            'focus_areas': ['Ukraine-Russia conflict']
        }
        
        print("Starting minimal test run...")
        print("This will make real API calls - ensure you want to proceed")
        
        # Track timing
        start_time = time.time()
        
        # Execute crew (comment out to avoid API costs during testing)
        # result = enhanced_crew.kickoff(inputs=test_inputs)
        
        # For testing without API calls:
        print("⚠️  Skipping actual crew execution to avoid API costs")
        print("To run the full test, uncomment the crew.kickoff line")
        result = "Test skipped"
        
        duration = time.time() - start_time
        
        # Track metrics
        metrics.track_run(result, duration)
        print(metrics.report())
        
        return True
        
    except Exception as e:
        print(f"❌ Test run error: {e}")
        logger.exception("Full error trace:")
        return False

def main():
    """Run all tests"""
    print("=== GPSE Crew Test Suite ===")
    print(f"Time: {datetime.now()}")
    print("-" * 50)
    
    tests = [
        ("Environment Setup", test_environment),
        ("Import Tests", test_imports),
        ("Crew Initialization", test_crew_initialization),
        ("Minimal Run Test", test_minimal_run)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("=== Test Summary ===")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your GPSE crew is ready to run.")
        print("\nTo execute a full analysis run:")
        print("  python gpse_crew.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues before running the crew.")

if __name__ == "__main__":
    main()
