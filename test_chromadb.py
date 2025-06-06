"""
Test ChromaDB functionality
"""

import os
import sys
from pathlib import Path

# Set ChromaDB environment variables BEFORE any imports
os.environ['ALLOW_RESET'] = 'TRUE'
os.environ['ANONYMIZED_TELEMETRY'] = 'FALSE'

try:
    import chromadb
    print(f"ChromaDB version: {chromadb.__version__}")
    
    # Create test directory
    test_dir = Path("chromadb_test")
    test_dir.mkdir(exist_ok=True)
    
    # Try to create a client
    print("Creating ChromaDB client...")
    client = chromadb.PersistentClient(path=str(test_dir))
    
    # Create a collection
    print("Creating test collection...")
    collection = client.create_collection("test_collection")
    
    # Add some data
    print("Adding test data...")
    collection.add(
        documents=["Test document 1", "Test document 2"],
        metadatas=[{"source": "test1"}, {"source": "test2"}],
        ids=["id1", "id2"]
    )
    
    # Query data
    print("Querying data...")
    results = collection.query(
        query_texts=["test"],
        n_results=2
    )
    
    print("Success! ChromaDB is working properly")
    print(f"Query results: {results}")
    
    # Clean up
    client.delete_collection("test_collection")
    
except Exception as e:
    print(f"ChromaDB test failed: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    
    print("\nTry downgrading ChromaDB:")
    print("pip install chromadb==0.3.29")
