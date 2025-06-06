"""
Minimal ChromaDB test to isolate permission issues
"""

import os
import chromadb
from pathlib import Path

def test_chromadb_locations():
    """Test ChromaDB in various locations to find what works"""
    
    test_locations = [
        "./test_chroma_local",
        str(Path.home() / "test_chroma_home"),
        str(Path(os.environ.get('TEMP', '/tmp')) / "test_chroma_temp"),
        "C:/temp/test_chroma" if os.name == 'nt' else "/tmp/test_chroma"
    ]
    
    for location in test_locations:
        print(f"\nTesting ChromaDB at: {location}")
        print("-" * 50)
        
        try:
            # Try to create parent directory if needed
            parent = Path(location).parent
            if not parent.exists():
                try:
                    parent.mkdir(parents=True, exist_ok=True)
                    print(f"Created parent directory: {parent}")
                except Exception as e:
                    print(f"Could not create parent directory: {e}")
                    continue
            
            # Test ChromaDB
            client = chromadb.PersistentClient(path=location)
            print("✓ Client created successfully")
            
            # Try to create a collection
            collection_name = "test_collection"
            try:
                client.delete_collection(collection_name)
            except:
                pass
            
            collection = client.create_collection(collection_name)
            print("✓ Collection created successfully")
            
            # Add a document
            collection.add(
                documents=["Test document"],
                ids=["test1"]
            )
            print("✓ Document added successfully")
            
            # Query
            results = collection.query(
                query_texts=["test"],
                n_results=1
            )
            print("✓ Query executed successfully")
            
            print(f"SUCCESS: ChromaDB works at {location}")
            
            # Clean up
            client.delete_collection(collection_name)
            
        except Exception as e:
            print(f"✗ FAILED: {type(e).__name__}: {str(e)}")

def test_crewai_default_location():
    """Test where CrewAI is trying to store ChromaDB by default"""
    print("\nChecking CrewAI default storage locations:")
    print("-" * 50)
    
    # Check environment variable
    storage_dir = os.environ.get('CREWAI_STORAGE_DIR')
    if storage_dir:
        print(f"CREWAI_STORAGE_DIR is set to: {storage_dir}")
    else:
        print("CREWAI_STORAGE_DIR is not set")
    
    # Check common locations
    app_name = "crewai"
    possible_locations = []
    
    if os.name == 'nt':  # Windows
        # Windows default locations
        appdata = os.environ.get('APPDATA')
        localappdata = os.environ.get('LOCALAPPDATA')
        
        if appdata:
            possible_locations.append(Path(appdata) / app_name)
        if localappdata:
            possible_locations.append(Path(localappdata) / app_name)
            
        # Also check current directory
        possible_locations.append(Path(".") / ".chroma")
        possible_locations.append(Path(".") / "chromadb")
    
    print("\nChecking possible default locations:")
    for loc in possible_locations:
        if loc.exists():
            print(f"  ✓ Found: {loc}")
            # Check permissions
            if os.access(loc, os.W_OK):
                print(f"    - Writable: Yes")
            else:
                print(f"    - Writable: No")
        else:
            print(f"  ✗ Not found: {loc}")

if __name__ == "__main__":
    print("ChromaDB Location Testing")
    print("=" * 50)
    
    # First check where CrewAI might be looking
    test_crewai_default_location()
    
    # Then test various locations
    test_chromadb_locations()
    
    print("\n" + "=" * 50)
    print("Testing complete!")
