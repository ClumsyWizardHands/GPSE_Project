"""
Windows-specific ChromaDB fix test for CrewAI
Applies all recommended Windows troubleshooting steps
"""

# CRITICAL: Apply pysqlite3-binary fix BEFORE any other imports
import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
print("✓ Applied pysqlite3-binary fix")

import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Set Windows-specific environment variables BEFORE importing CrewAI/ChromaDB
os.environ["CHROMA_SEGMENT_MANAGER_IMPL"] = "local"
os.environ["SQLITE_TMPDIR"] = tempfile.gettempdir()

# Use a short path to avoid MAX_PATH issues on Windows
short_base_path = "C:\\gpse_data"
os.environ["CREWAI_STORAGE_DIR"] = short_base_path

print(f"✓ Set CREWAI_STORAGE_DIR to: {short_base_path}")
print(f"✓ Set SQLITE_TMPDIR to: {tempfile.gettempdir()}")

# Now import CrewAI and ChromaDB
from crewai import Agent, Task, Crew
import chromadb
from chromadb.config import Settings

def ensure_directory_exists(path):
    """Create directory with proper Windows permissions"""
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {path}")
    return str(path)

def test_chromadb_direct():
    """Test ChromaDB directly to ensure it works"""
    print("\n=== Testing ChromaDB Directly ===")
    try:
        # Use raw string for Windows path
        test_path = r"C:\gpse_data\test_direct"
        ensure_directory_exists(test_path)
        
        # Create ChromaDB client with Windows-friendly settings
        client = chromadb.PersistentClient(
            path=test_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
                is_persistent=True
            )
        )
        
        # Test basic operations
        collection = client.get_or_create_collection("test_collection")
        collection.add(
            documents=["Test document"],
            ids=["test1"]
        )
        
        results = collection.query(
            query_texts=["test"],
            n_results=1
        )
        
        print("✓ ChromaDB direct test passed")
        print(f"  - Client path: {test_path}")
        print(f"  - Collection count: {collection.count()}")
        
        # Clean up
        client.delete_collection("test_collection")
        return True
        
    except Exception as e:
        print(f"✗ ChromaDB direct test failed: {e}")
        return False

def test_crewai_memory():
    """Test CrewAI with memory using Windows fixes"""
    print("\n=== Testing CrewAI with Memory (Windows Fixes Applied) ===")
    
    try:
        # Ensure the short path exists
        ensure_directory_exists(short_base_path)
        
        # Create a simple agent with memory enabled
        test_agent = Agent(
            role="Test Agent",
            goal="Test memory functionality",
            backstory="A test agent for debugging ChromaDB issues on Windows",
            memory=True,  # Enable memory
            verbose=True,
            allow_delegation=False
        )
        
        # Create a simple task
        test_task = Task(
            description="Simply return 'Memory test successful'",
            agent=test_agent,
            expected_output="A simple test message"
        )
        
        # Create crew with the memory-enabled agent
        crew = Crew(
            agents=[test_agent],
            tasks=[test_task],
            verbose=True,
            memory=True  # Enable crew memory
        )
        
        # Execute the crew
        print("\nExecuting crew...")
        result = crew.kickoff()
        
        print("\n✓ CrewAI memory test passed!")
        print(f"Result: {result}")
        return True
        
    except Exception as e:
        print(f"\n✗ CrewAI memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_sqlite_version():
    """Check SQLite version being used"""
    print("\n=== SQLite Version Check ===")
    import sqlite3
    print(f"SQLite version: {sqlite3.sqlite_version}")
    print(f"SQLite module: {sqlite3.__name__}")
    print(f"SQLite file: {sqlite3.__file__ if hasattr(sqlite3, '__file__') else 'N/A'}")

def test_path_variations():
    """Test different path formats for Windows compatibility"""
    print("\n=== Testing Path Variations ===")
    
    path_tests = [
        ("Raw string short", r"C:\gpse"),
        ("Forward slashes", "C:/gpse_data"),
        ("os.path.join", os.path.join("C:", "gpse_data")),
        ("Temp directory", os.path.join(tempfile.gettempdir(), "gpse_data")),
        ("User profile", os.path.join(os.path.expanduser("~"), "gpse_data"))
    ]
    
    for name, path in path_tests:
        print(f"\nTesting: {name}")
        print(f"Path: {path}")
        
        try:
            # Set environment variable
            os.environ["CREWAI_STORAGE_DIR"] = path
            
            # Ensure directory exists
            ensure_directory_exists(path)
            
            # Quick test with a minimal agent
            agent = Agent(
                role="Path Test",
                goal="Test path",
                backstory="Testing paths",
                memory=True,
                verbose=False
            )
            
            print(f"✓ Path test passed: {name}")
            
        except Exception as e:
            print(f"✗ Path test failed: {name} - {str(e)[:100]}")

def main():
    """Run all Windows-specific tests"""
    print("=" * 60)
    print("Windows ChromaDB Fix Test Suite")
    print("=" * 60)
    
    # Check SQLite version first
    check_sqlite_version()
    
    # Test ChromaDB directly
    direct_success = test_chromadb_direct()
    
    if direct_success:
        # Test different path formats
        test_path_variations()
        
        # Test CrewAI with memory
        crewai_success = test_crewai_memory()
        
        if crewai_success:
            print("\n✅ ALL TESTS PASSED! Windows fixes work!")
            print("\nRecommended configuration:")
            print(f"- Use pysqlite3-binary import fix")
            print(f"- Set CREWAI_STORAGE_DIR to: {short_base_path}")
            print(f"- Set CHROMA_SEGMENT_MANAGER_IMPL to: local")
        else:
            print("\n⚠️ ChromaDB works but CrewAI memory still fails")
            print("This confirms it's a CrewAI-specific issue on Windows")
    else:
        print("\n❌ Even direct ChromaDB fails - check installation")

if __name__ == "__main__":
    main()
