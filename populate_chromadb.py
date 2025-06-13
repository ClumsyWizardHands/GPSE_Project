#!/usr/bin/env python3
"""
Populate ChromaDB with existing strategy analyses
This script processes all existing strategy analysis files and adds them to ChromaDB
"""

import os
import logging
from pathlib import Path
from db_manager import ChromaDBManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def populate_chromadb():
    """Process all existing strategy analyses and add them to ChromaDB"""
    
    # Initialize ChromaDB manager
    db_manager = ChromaDBManager(
        collection_name='grand_strategy',
        db_path='./strategy_db_chroma'
    )
    
    # Strategy analyses directory
    strategy_dir = Path('strategy_analyses')
    
    if not strategy_dir.exists():
        logger.error(f"Strategy analyses directory not found: {strategy_dir}")
        return
    
    # Get all markdown files
    md_files = list(strategy_dir.glob('*.md'))
    
    print(f"\nFound {len(md_files)} strategy analysis files to process")
    print("="*60)
    
    total_chunks = 0
    processed_files = 0
    
    for md_file in md_files:
        print(f"\nProcessing: {md_file.name}")
        
        try:
            # Process the document and add to ChromaDB
            chunks_added = db_manager.process_strategy_document(str(md_file))
            
            if chunks_added > 0:
                print(f"✓ Successfully added {chunks_added} chunks")
                total_chunks += chunks_added
                processed_files += 1
            else:
                print(f"✗ No chunks added (file may be improperly formatted)")
                
        except Exception as e:
            logger.error(f"Error processing {md_file.name}: {str(e)}")
            print(f"✗ Error: {str(e)}")
    
    print("\n" + "="*60)
    print(f"Population complete!")
    print(f"Files processed: {processed_files}/{len(md_files)}")
    print(f"Total chunks added: {total_chunks}")
    
    # Test the populated database
    print("\n" + "="*60)
    print("Testing database with sample queries...")
    
    test_queries = [
        "China strategic competition",
        "Russia Ukraine conflict",
        "Middle East tensions",
        "cyber warfare AI",
        "climate change security"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = db_manager.query_db(query, n_results=2)
        
        if results['documents'] and results['documents'][0]:
            print(f"Found {len(results['documents'][0])} relevant results")
            for i, doc in enumerate(results['documents'][0]):
                preview = doc[:100] + "..." if len(doc) > 100 else doc
                metadata = results['metadatas'][0][i] if results['metadatas'][0] else {}
                date = metadata.get('date', 'Unknown date')
                print(f"  [{date}] {preview}")
        else:
            print("  No results found")

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("ChromaDB Population Tool")
    print("Processing existing strategy analyses...")
    print("="*60)
    
    try:
        populate_chromadb()
        print("\n✓ ChromaDB population completed successfully!")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"\n✗ Fatal error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
