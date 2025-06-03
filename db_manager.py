"""
Database manager for ChromaDB with sentence-transformer embeddings.
This module provides functions to add text to and query from a vector database.
"""

import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the sentence transformer model globally to avoid repeated loading
MODEL_NAME = 'all-MiniLM-L6-v2'
_model = None

def get_model():
    """Get or initialize the sentence transformer model."""
    global _model
    if _model is None:
        logger.info(f"Loading SentenceTransformer model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def add_text_to_db(
    text_content: str,
    document_id: str,
    collection_name: str = 'grand_strategy',
    db_path: str = './strategy_db_chroma'
) -> bool:
    """
    Add text content to ChromaDB with embeddings.
    
    Args:
        text_content: The text to add to the database
        document_id: Unique identifier for the document
        collection_name: Name of the ChromaDB collection (default: 'grand_strategy')
        db_path: Path to the ChromaDB persistent storage (default: './strategy_db_chroma')
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Initialize persistent ChromaDB client
        client = chromadb.PersistentClient(path=db_path)
        
        # Get or create collection
        collection = client.get_or_create_collection(name=collection_name)
        
        # Get the sentence transformer model
        model = get_model()
        
        # Create embedding for the text content
        logger.info(f"Creating embedding for document: {document_id}")
        embedding = model.encode(text_content).tolist()
        
        # Add to collection
        collection.add(
            documents=[text_content],
            embeddings=[embedding],
            ids=[document_id],
            metadatas=[{"document_id": document_id}]
        )
        
        logger.info(f"Successfully added document {document_id} to collection {collection_name}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding text to database: {str(e)}")
        return False


def query_db(
    query_text: str,
    n_results: int = 3,
    collection_name: str = 'grand_strategy',
    db_path: str = './strategy_db_chroma'
) -> List[str]:
    """
    Query the ChromaDB for similar documents.
    
    Args:
        query_text: The text to search for
        n_results: Number of results to return (default: 3)
        collection_name: Name of the ChromaDB collection (default: 'grand_strategy')
        db_path: Path to the ChromaDB persistent storage (default: './strategy_db_chroma')
    
    Returns:
        List[str]: List of retrieved document texts, empty list if error
    """
    try:
        # Initialize persistent ChromaDB client
        client = chromadb.PersistentClient(path=db_path)
        
        # Get collection
        try:
            collection = client.get_collection(name=collection_name)
        except Exception:
            logger.warning(f"Collection '{collection_name}' not found")
            return []
        
        # Get the sentence transformer model
        model = get_model()
        
        # Create embedding for the query
        logger.info(f"Creating embedding for query: {query_text[:50]}...")
        query_embedding = model.encode(query_text).tolist()
        
        # Query the collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Extract and return the documents
        if results and 'documents' in results and results['documents']:
            documents = results['documents'][0]  # Results are nested in a list
            logger.info(f"Found {len(documents)} matching documents")
            return documents
        else:
            logger.info("No matching documents found")
            return []
        
    except Exception as e:
        logger.error(f"Error querying database: {str(e)}")
        return []


def process_strategy_document(file_path: str) -> None:
    """
    Read a strategy analysis document and add it to the database in chunks.
    
    Args:
        file_path: Path to the markdown file containing strategy analysis
    """
    import os
    import re
    
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract the Entry ID from the content
        entry_id_match = re.search(r'\*\*Entry ID:\*\* ([\w-]+)', content)
        base_id = entry_id_match.group(1) if entry_id_match else os.path.basename(file_path).replace('.md', '')
        
        # Split the document into chunks based on major sections
        chunks = []
        
        # Extract Executive Summary
        exec_summary_match = re.search(r'### Executive Summary\n\n(.+?)\n---', content, re.DOTALL)
        if exec_summary_match:
            chunks.append({
                'id': f'{base_id}-executive-summary',
                'text': f'Executive Summary: {exec_summary_match.group(1).strip()}',
                'section': 'Executive Summary'
            })
        
        # Extract each country/power analysis
        country_sections = re.findall(r'#### \d+\. \*\*(.+?):\s*(.+?)\*\*\n\n(.+?)(?=#### \d+\.|### |---|$)', content, re.DOTALL)
        for i, (country, subtitle, analysis) in enumerate(country_sections):
            chunk_text = f'{country}: {subtitle}\n\n{analysis.strip()}'
            chunks.append({
                'id': f'{base_id}-{country.lower().replace(" ", "-").replace(":", "")}-analysis',
                'text': chunk_text,
                'section': f'{country} Analysis'
            })
        
        # Extract Scenario Implications
        scenario_match = re.search(r'### Scenario Implications\n\n(.+?)(?=---|$)', content, re.DOTALL)
        if scenario_match:
            chunks.append({
                'id': f'{base_id}-scenario-implications',
                'text': f'Scenario Implications:\n{scenario_match.group(1).strip()}',
                'section': 'Scenario Implications'
            })
        
        # Add each chunk to the database
        print(f"\nProcessing strategy document: {file_path}")
        print(f"Found {len(chunks)} chunks to add to database\n")
        
        for chunk in chunks:
            success = add_text_to_db(chunk['text'], chunk['id'])
            if success:
                print(f"✓ Added chunk: {chunk['id']} ({chunk['section']})")
            else:
                print(f"✗ Failed to add chunk: {chunk['id']}")
        
        print(f"\nCompleted processing {file_path}")
        
    except Exception as e:
        logger.error(f"Error processing strategy document: {str(e)}")


class ChromaDBManager:
    """Wrapper class for ChromaDB operations."""
    
    def __init__(self, collection_name: str = 'grand_strategy', db_path: str = './strategy_db_chroma'):
        self.collection_name = collection_name
        self.db_path = db_path
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.model = get_model()
    
    def add_text_to_db(self, text_content: str, document_id: str, metadata: Dict[str, Any] = None) -> bool:
        """Add text to the database."""
        try:
            embedding = self.model.encode(text_content).tolist()
            
            # Prepare metadata
            doc_metadata = {"document_id": document_id}
            if metadata:
                doc_metadata.update(metadata)
            
            self.collection.add(
                documents=[text_content],
                embeddings=[embedding],
                ids=[document_id],
                metadatas=[doc_metadata]
            )
            
            logger.info(f"Successfully added document {document_id} to collection {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding text to database: {str(e)}")
            return False
    
    def query_db(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """Query the database for similar documents."""
        try:
            query_embedding = self.model.encode(query_text).tolist()
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying database: {str(e)}")
            return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
    
    def process_strategy_document(self, file_path: str) -> int:
        """Process a strategy document and add it to the database in chunks."""
        import os
        import re
        from datetime import datetime
        
        chunks_added = 0
        
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata
            entry_id_match = re.search(r'\*\*Entry ID:\*\* ([\w-]+)', content)
            date_match = re.search(r'\*\*Date:\*\* (.+?)\n', content)
            
            base_id = entry_id_match.group(1) if entry_id_match else os.path.basename(file_path).replace('.md', '')
            date_str = date_match.group(1) if date_match else datetime.now().strftime("%B %d, %Y")
            
            # Split the document into chunks based on major sections
            chunks = []
            
            # Extract Executive Summary
            exec_summary_match = re.search(r'### Executive Summary\n\n(.+?)\n---', content, re.DOTALL)
            if exec_summary_match:
                chunks.append({
                    'id': f'{base_id}-executive-summary',
                    'text': f'Executive Summary: {exec_summary_match.group(1).strip()}',
                    'section': 'Executive Summary',
                    'date': date_str
                })
            
            # Extract each country/power analysis
            country_sections = re.findall(r'#### \d+\. \*\*(.+?):\s*(.+?)\*\*\n\n(.+?)(?=#### \d+\.|### |---|$)', content, re.DOTALL)
            for i, (country, subtitle, analysis) in enumerate(country_sections):
                chunk_text = f'{country}: {subtitle}\n\n{analysis.strip()}'
                chunks.append({
                    'id': f'{base_id}-{country.lower().replace(" ", "-").replace(":", "")}-analysis',
                    'text': chunk_text,
                    'section': f'{country} Analysis',
                    'date': date_str
                })
            
            # Extract Scenario Implications
            scenario_match = re.search(r'### Scenario Implications\n\n(.+?)(?=---|$)', content, re.DOTALL)
            if scenario_match:
                chunks.append({
                    'id': f'{base_id}-scenario-implications',
                    'text': f'Scenario Implications:\n{scenario_match.group(1).strip()}',
                    'section': 'Scenario Implications',
                    'date': date_str
                })
            
            # Add each chunk to the database
            logger.info(f"Processing strategy document: {file_path}")
            logger.info(f"Found {len(chunks)} chunks to add to database")
            
            for chunk in chunks:
                metadata = {
                    'document_id': base_id,
                    'section': chunk['section'],
                    'date': chunk['date']
                }
                success = self.add_text_to_db(chunk['text'], chunk['id'], metadata)
                if success:
                    chunks_added += 1
                    logger.info(f"Added chunk: {chunk['id']} ({chunk['section']})")
                else:
                    logger.error(f"Failed to add chunk: {chunk['id']}")
            
            logger.info(f"Completed processing {file_path}, added {chunks_added} chunks")
            return chunks_added
            
        except Exception as e:
            logger.error(f"Error processing strategy document: {str(e)}")
            return chunks_added


# Example usage and testing
if __name__ == "__main__":
    # Process the strategy analysis document
    import os
    
    # Check if strategy_analyses directory exists and process files
    strategy_dir = 'strategy_analyses'
    if os.path.exists(strategy_dir):
        for filename in os.listdir(strategy_dir):
            if filename.endswith('.md'):
                file_path = os.path.join(strategy_dir, filename)
                process_strategy_document(file_path)
    
    # Test querying the database
    print("\n" + "="*50 + "\n")
    print("Testing database queries on the imported content:\n")
    
    test_queries = [
        "What is China's AI strategy?",
        "Tell me about India's diplomatic position",
        "What are the flashpoint risks?",
        "Russia strategic ambiguity",
        "US internal tensions"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = query_db(query, n_results=2)
        for i, result in enumerate(results):
            preview = result[:150] + '...' if len(result) > 150 else result
            print(f"  Result {i+1}: {preview}")
