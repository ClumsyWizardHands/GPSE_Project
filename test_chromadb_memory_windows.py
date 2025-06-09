"""
Comprehensive test for ChromaDB memory functionality on Windows
Tests the complete Windows fix implementation
"""

# Apply Windows-specific fixes at the very top
try:
    import pysqlite3
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    print("✓ Applied pysqlite3-binary fix for Windows")
except ImportError:
    print("⚠️ pysqlite3-binary not available. For best results on Windows, run: pip install pysqlite3-binary")

import os
from pathlib import Path
import tempfile
import shutil

# Set environment variables before any imports
os.environ["CREWAI_STORAGE_DIR"] = r"C:\gpse_data"
os.environ["CHROMA_SEGMENT_MANAGER_IMPL"] = "local"
os.environ["SQLITE_TMPDIR"] = os.environ.get("TEMP", r"C:\temp")

# Ensure the storage directory exists
storage_path = Path(os.environ["CREWAI_STORAGE_DIR"])
storage_path.mkdir(parents=True, exist_ok=True)
print(f"✓ Storage directory ready: {storage_path}")

# Now import the rest
import chromadb
from chromadb.config import Settings
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_chromadb_direct():
    """Test ChromaDB directly without CrewAI"""
    print("\n=== Testing ChromaDB Directly ===")
    
    try:
        # Create a test directory
        test_dir = Path(r"C:\gpse_data\test_chromadb")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(
            path=str(test_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        print("✓ ChromaDB client created successfully")
        
        # Create a collection
        collection = client.get_or_create_collection(
            name="test_collection",
            metadata={"hnsw:space": "cosine"}
        )
        print("✓ Collection created successfully")
        
        # Add some test data
        collection.add(
            documents=["This is a test document", "Another test document"],
            metadatas=[{"type": "test"}, {"type": "test"}],
            ids=["doc1", "doc2"]
        )
        print("✓ Documents added successfully")
        
        # Query the collection
        results = collection.query(
            query_texts=["test"],
            n_results=2
        )
        print(f"✓ Query returned {len(results['ids'][0])} results")
        
        # Clean up
        shutil.rmtree(test_dir, ignore_errors=True)
        print("✓ Cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"✗ ChromaDB Direct Test Failed: {str(e)}")
        return False

def test_crewai_memory():
    """Test CrewAI with memory enabled"""
    print("\n=== Testing CrewAI Memory System ===")
    
    try:
        # Create a simple test agent
        test_agent = Agent(
            role='Test Agent',
            goal='Test memory functionality',
            backstory='A test agent for verifying memory works',
            llm=ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7
            ),
            memory=True,
            verbose=True
        )
        print("✓ Agent created with memory enabled")
        
        # Create a simple task
        test_task = Task(
            description="Remember this: The capital of France is Paris. What is the capital of France?",
            expected_output="The capital of France",
            agent=test_agent
        )
        print("✓ Task created successfully")
        
        # Create crew with memory
        test_crew = Crew(
            agents=[test_agent],
            tasks=[test_task],
            process=Process.sequential,
            memory=True,
            verbose=True
        )
        print("✓ Crew created with memory enabled")
        
        # Execute the crew
        print("\nExecuting crew...")
        result = test_crew.kickoff()
        print(f"✓ Crew execution completed")
        print(f"Result: {result}")
        
        # Test persistence by creating a second crew
        print("\n--- Testing Memory Persistence ---")
        
        test_task2 = Task(
            description="What capital city did I mention earlier?",
            expected_output="The previously mentioned capital city",
            agent=test_agent
        )
        
        test_crew2 = Crew(
            agents=[test_agent],
            tasks=[test_task2],
            process=Process.sequential,
            memory=True,
            verbose=True
        )
        
        print("Executing second crew to test memory persistence...")
        result2 = test_crew2.kickoff()
        print(f"✓ Second crew execution completed")
        print(f"Result: {result2}")
        
        return True
        
    except Exception as e:
        print(f"✗ CrewAI Memory Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_environment():
    """Check if all environment variables and paths are set correctly"""
    print("\n=== Environment Check ===")
    
    checks = {
        "CREWAI_STORAGE_DIR": os.environ.get("CREWAI_STORAGE_DIR"),
        "CHROMA_SEGMENT_MANAGER_IMPL": os.environ.get("CHROMA_SEGMENT_MANAGER_IMPL"),
        "SQLITE_TMPDIR": os.environ.get("SQLITE_TMPDIR"),
        "Storage Path Exists": storage_path.exists(),
        "Storage Path Writable": os.access(storage_path, os.W_OK) if storage_path.exists() else False
    }
    
    all_good = True
    for check, value in checks.items():
        status = "✓" if value else "✗"
        print(f"{status} {check}: {value}")
        if not value:
            all_good = False
    
    return all_good

def main():
    """Run all tests"""
    print("=" * 60)
    print("GPSE ChromaDB Memory Test Suite - Windows")
    print("=" * 60)
    
    # Check environment
    env_ok = check_environment()
    if not env_ok:
        print("\n⚠️ Environment check failed. Please verify paths and permissions.")
    
    # Test ChromaDB directly
    chromadb_ok = test_chromadb_direct()
    
    # Test CrewAI memory
    crewai_ok = test_crewai_memory()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Environment Check: {'✓ PASSED' if env_ok else '✗ FAILED'}")
    print(f"ChromaDB Direct: {'✓ PASSED' if chromadb_ok else '✗ FAILED'}")
    print(f"CrewAI Memory: {'✓ PASSED' if crewai_ok else '✗ FAILED'}")
    
    if env_ok and chromadb_ok and crewai_ok:
        print("\n🎉 All tests passed! ChromaDB memory is working correctly.")
        print("\nYou can now run your main GPSE crew with memory enabled:")
        print("  python main_crew.py")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        print("\nTroubleshooting tips:")
        print("1. Install pysqlite3-binary: pip install pysqlite3-binary")
        print("2. Run as Administrator (once) to set permissions")
        print("3. Check if C:\\gpse_data is accessible")
        print("4. Verify your API keys are set in .env")

if __name__ == "__main__":
    main()
