"""
Test ChromaDB with new configuration
Verifies ChromaDB 0.5.x+ works without deprecated settings
"""

import chromadb
from chromadb.config import Settings
import sys
from pathlib import Path

def test_chromadb():
    """Test ChromaDB functionality with new API"""
    print("Testing ChromaDB with new configuration...")
    print("-" * 50)
    
    try:
        # 1. Create client with minimal configuration
        print("1. Creating ChromaDB client...")
        client = chromadb.PersistentClient(path="./chroma_test_new")
        print("   ✓ Client created successfully")
        
        # 2. Create a collection
        print("\n2. Creating test collection...")
        # Delete collection if it exists
        try:
            client.delete_collection("test_collection")
        except:
            pass
        
        collection = client.create_collection(
            name="test_collection",
            metadata={"description": "Test collection for GPSE"}
        )
        print("   ✓ Collection created successfully")
        
        # 3. Add test documents
        print("\n3. Adding test documents...")
        documents = [
            "The Ukraine-Russia conflict continues with new developments.",
            "US-China relations show signs of tension over trade policies.",
            "Middle East tensions escalate as regional powers negotiate."
        ]
        
        ids = ["doc1", "doc2", "doc3"]
        
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=[
                {"topic": "Ukraine-Russia", "date": "2025-06-03"},
                {"topic": "US-China", "date": "2025-06-03"},
                {"topic": "Middle East", "date": "2025-06-03"}
            ]
        )
        print(f"   ✓ Added {len(documents)} documents")
        
        # 4. Query the collection
        print("\n4. Querying collection...")
        results = collection.query(
            query_texts=["What are the current geopolitical tensions?"],
            n_results=2
        )
        print("   ✓ Query executed successfully")
        print(f"   Found {len(results['documents'][0])} relevant documents")
        
        # 5. Test persistence
        print("\n5. Testing persistence...")
        # Get collection again
        collection2 = client.get_collection("test_collection")
        count = collection2.count()
        print(f"   ✓ Collection persisted with {count} documents")
        
        # 6. Clean up (optional)
        print("\n6. Cleanup...")
        client.delete_collection("test_collection")
        print("   ✓ Test collection deleted")
        
        print("\n" + "=" * 50)
        print("SUCCESS: ChromaDB is working correctly!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_chromadb_version():
    """Check ChromaDB version"""
    try:
        import chromadb
        print(f"ChromaDB version: {chromadb.__version__}")
    except:
        print("Could not determine ChromaDB version")

if __name__ == "__main__":
    print("ChromaDB New Configuration Test")
    print("=" * 50)
    
    check_chromadb_version()
    print()
    
    success = test_chromadb()
    
    if success:
        print("\nChromaDB is ready for use with CrewAI!")
        print("You can now run: python main_crew_chromadb_clean.py")
    else:
        print("\nChromaDB test failed. Please check the error messages above.")
        sys.exit(1)
