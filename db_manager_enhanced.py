"""
Enhanced Database manager for ChromaDB with sentence-transformer embeddings.
This module provides functions to add text to and query from a vector database.
Supports both legacy and new enhanced analysis formats.
"""

import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import logging
import re
import os
from datetime import datetime
import json
from schemas import StrategicPathway, PathwayUpdate

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


class ChromaDBManager:
    """Enhanced wrapper class for ChromaDB operations supporting multiple document formats."""
    
    def __init__(self, db_path: str = './strategy_db_chroma'):
        self.db_path = db_path
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name='grand_strategy')
        self.pathways_collection = self.client.get_or_create_collection(name='strategic_pathways')
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
            
            logger.info(f"Successfully added document {document_id} to collection {self.collection.name}")
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

    def add_pathway(self, pathway_data: StrategicPathway) -> bool:
        """Adds a StrategicPathway object to the database."""
        try:
            # Serialize the object to a JSON string for storage as the document
            doc_json = pathway_data.model_dump_json()
            
            # The text to be embedded is a combination of title, description, and indicators
            text_to_embed = f"Title: {pathway_data.title}\nDescription: {pathway_data.description}\nIndicators: {', '.join(pathway_data.indicators)}"
            embedding = self.model.encode(text_to_embed).tolist()
            
            self.pathways_collection.add(
                documents=[doc_json],
                embeddings=[embedding],
                ids=[pathway_data.pathway_id],
                metadatas=[pathway_data.model_dump()] # Store the whole object as metadata as well
            )
            logger.info(f"Successfully added pathway {pathway_data.pathway_id} to collection 'strategic_pathways'")
            return True
        except Exception as e:
            logger.error(f"Error adding pathway to database: {str(e)}")
            return False

    def update_pathway(self, pathway_id: str, update_data: PathwayUpdate) -> bool:
        """Updates an existing pathway with a new update event."""
        try:
            # Retrieve the existing pathway
            existing_pathway_doc = self.pathways_collection.get(ids=[pathway_id])
            if not existing_pathway_doc['documents']:
                logger.error(f"Pathway with ID {pathway_id} not found.")
                return False
            
            # Deserialize, update, and re-serialize
            pathway = StrategicPathway.model_validate_json(existing_pathway_doc['documents'][0])
            pathway.updates.append(update_data)
            pathway.last_updated = datetime.now().date()
            
            # Now upsert the updated object
            doc_json = pathway.model_dump_json()
            text_to_embed = f"Title: {pathway.title}\nDescription: {pathway.description}\nIndicators: {', '.join(pathway.indicators)}"
            embedding = self.model.encode(text_to_embed).tolist()

            self.pathways_collection.upsert(
                documents=[doc_json],
                embeddings=[embedding],
                ids=[pathway.pathway_id],
                metadatas=[pathway.model_dump()]
            )
            logger.info(f"Successfully updated pathway {pathway_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating pathway {pathway_id}: {str(e)}")
            return False

    def find_relevant_pathways(self, event_summary: str, key_actors: List[str], n_results: int = 3) -> List[StrategicPathway]:
        """Finds relevant pathways based on an event summary and key actors."""
        try:
            query_text = f"Event: {event_summary}\nActors: {', '.join(key_actors)}"
            query_embedding = self.model.encode(query_text).tolist()
            
            results = self.pathways_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            pathways = [StrategicPathway.model_validate_json(doc) for doc in results['documents'][0]]
            return pathways
        except Exception as e:
            logger.error(f"Error finding relevant pathways: {str(e)}")
            return []
    
    def detect_document_format(self, content: str) -> str:
        """Detect whether document is legacy or enhanced format."""
        # Check for enhanced format markers
        if '## EXECUTIVE SUMMARY' in content or '## STRATEGIC SITUATION ASSESSMENT' in content:
            return 'enhanced'
        # Check for legacy format markers
        elif '### Executive Summary' in content or '#### 1. **' in content:
            return 'legacy'
        else:
            return 'unknown'
    
    def process_enhanced_format(self, content: str, base_id: str, date_str: str) -> List[Dict[str, Any]]:
        """Process enhanced format documents (new GPSE format)."""
        chunks = []
        
        # Extract Executive Summary
        exec_match = re.search(r'## EXECUTIVE SUMMARY\n\n(.+?)(?=\n## |\n---|\Z)', content, re.DOTALL)
        if exec_match:
            chunks.append({
                'id': f'{base_id}-executive-summary',
                'text': f'Executive Summary:\n{exec_match.group(1).strip()}',
                'section': 'Executive Summary',
                'date': date_str
            })
        
        # Extract Learning from Past Assessments
        learning_match = re.search(r'## LEARNING FROM PAST ASSESSMENTS\n\n(.+?)(?=\n## |\n---|\Z)', content, re.DOTALL)
        if learning_match:
            chunks.append({
                'id': f'{base_id}-learning-past',
                'text': f'Learning from Past Assessments:\n{learning_match.group(1).strip()}',
                'section': 'Learning from Past Assessments',
                'date': date_str
            })
        
        # Extract Strategic Situation Assessment
        situation_match = re.search(r'## STRATEGIC SITUATION ASSESSMENT\n\n(.+?)(?=\n## |\n---|\Z)', content, re.DOTALL)
        if situation_match:
            chunks.append({
                'id': f'{base_id}-strategic-situation',
                'text': f'Strategic Situation Assessment:\n{situation_match.group(1).strip()}',
                'section': 'Strategic Situation Assessment',
                'date': date_str
            })
        
        # Extract Priority Developments
        priority_match = re.search(r'## PRIORITY DEVELOPMENTS ANALYSIS\n\n(.+?)(?=\n## |\n---|\Z)', content, re.DOTALL)
        if priority_match:
            # Try to split by numbered sections
            priority_text = priority_match.group(1)
            priority_sections = re.split(r'### \d+\. ', priority_text)
            
            if len(priority_sections) > 1:
                for i, section in enumerate(priority_sections[1:], 1):
                    section_title_match = re.match(r'^(.+?)\n', section)
                    if section_title_match:
                        title = section_title_match.group(1).strip()
                        chunks.append({
                            'id': f'{base_id}-priority-{i}',
                            'text': f'Priority Development: {title}\n{section.strip()}',
                            'section': f'Priority Development {i}',
                            'date': date_str
                        })
            else:
                chunks.append({
                    'id': f'{base_id}-priority-developments',
                    'text': f'Priority Developments:\n{priority_text.strip()}',
                    'section': 'Priority Developments',
                    'date': date_str
                })
        
        # Extract Scenario Analysis
        scenario_match = re.search(r'## SCENARIO ANALYSIS\n\n(.+?)(?=\n## |\n---|\Z)', content, re.DOTALL)
        if scenario_match:
            scenario_text = scenario_match.group(1)
            # Try to split by scenario numbers
            scenarios = re.split(r'### Scenario \d+:', scenario_text)
            
            if len(scenarios) > 1:
                for i, scenario in enumerate(scenarios[1:], 1):
                    chunks.append({
                        'id': f'{base_id}-scenario-{i}',
                        'text': f'Scenario {i}:\n{scenario.strip()}',
                        'section': f'Scenario {i}',
                        'date': date_str
                    })
            else:
                chunks.append({
                    'id': f'{base_id}-scenarios',
                    'text': f'Scenario Analysis:\n{scenario_text.strip()}',
                    'section': 'Scenario Analysis',
                    'date': date_str
                })
        
        # Extract Strategic Recommendations
        recommendations_match = re.search(r'## STRATEGIC RECOMMENDATIONS\n\n(.+?)(?=\n## |\n---|\Z)', content, re.DOTALL)
        if recommendations_match:
            chunks.append({
                'id': f'{base_id}-recommendations',
                'text': f'Strategic Recommendations:\n{recommendations_match.group(1).strip()}',
                'section': 'Strategic Recommendations',
                'date': date_str
            })
        
        return chunks
    
    def process_legacy_format(self, content: str, base_id: str, date_str: str) -> List[Dict[str, Any]]:
        """Process legacy format documents (original GPSE format)."""
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
        
        return chunks
    
    def process_strategy_document(self, file_path: str) -> int:
        """Process a strategy document and add it to the database in chunks."""
        chunks_added = 0
        
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata
            entry_id_match = re.search(r'\*\*Entry ID:\*\* ([\w-]+)', content)
            date_match = re.search(r'\*\*Date:\*\* (.+?)\n', content)
            
            # Try to extract date from filename if not in content
            if not date_match:
                filename_date_match = re.search(r'GGSM-(.+?)-', os.path.basename(file_path))
                if filename_date_match:
                    date_str = filename_date_match.group(1)
                else:
                    date_str = datetime.now().strftime("%B %d, %Y")
            else:
                date_str = date_match.group(1)
            
            base_id = entry_id_match.group(1) if entry_id_match else os.path.basename(file_path).replace('.md', '')
            
            # Detect document format
            doc_format = self.detect_document_format(content)
            logger.info(f"Detected document format: {doc_format}")
            
            # Process based on format
            if doc_format == 'enhanced':
                chunks = self.process_enhanced_format(content, base_id, date_str)
            elif doc_format == 'legacy':
                chunks = self.process_legacy_format(content, base_id, date_str)
            else:
                logger.warning(f"Unknown document format for {file_path}, attempting generic chunking")
                # Generic chunking by major sections (##)
                chunks = []
                sections = re.split(r'\n## ', content)
                for i, section in enumerate(sections):
                    if section.strip():
                        title_match = re.match(r'^(.+?)\n', section)
                        title = title_match.group(1) if title_match else f'Section {i}'
                        chunks.append({
                            'id': f'{base_id}-section-{i}',
                            'text': section.strip(),
                            'section': title,
                            'date': date_str
                        })
            
            # Add each chunk to the database
            logger.info(f"Processing strategy document: {file_path}")
            logger.info(f"Found {len(chunks)} chunks to add to database")
            
            for chunk in chunks:
                metadata = {
                    'document_id': base_id,
                    'section': chunk['section'],
                    'date': chunk['date'],
                    'format': doc_format
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


# Convenience functions for backward compatibility
def add_text_to_db(
    text_content: str,
    document_id: str,
    db_path: str = './strategy_db_chroma'
) -> bool:
    """Add text content to ChromaDB with embeddings."""
    manager = ChromaDBManager(db_path)
    return manager.add_text_to_db(text_content, document_id)


def query_db(
    query_text: str,
    n_results: int = 3,
    db_path: str = './strategy_db_chroma'
) -> List[str]:
    """Query the ChromaDB for similar documents."""
    manager = ChromaDBManager(db_path)
    results = manager.query_db(query_text, n_results)
    
    if results and 'documents' in results and results['documents']:
        documents = results['documents'][0]
        return documents
    else:
        return []


def process_strategy_document(file_path: str) -> None:
    """Process a strategy document and add it to the database."""
    manager = ChromaDBManager()
    manager.process_strategy_document(file_path)


# Example usage and testing
if __name__ == "__main__":
    # Process the strategy analysis documents
    import os
    
    manager = ChromaDBManager()
    
    # Check if strategy_analyses directory exists and process files
    strategy_dir = 'strategy_analyses'
    if os.path.exists(strategy_dir):
        # Process specific enhanced format files first
        enhanced_files = [
            'GGSM-June 13, 2025-EnhancedMemoryAnalysis.md',
            'GGSM-June 13, 2025-MemoryEnhancedAnalysis.md',
            'GGSM-June 12, 2025-ImprovedAnalysis.md',
            'GGSM-June 12, 2025-DirectAnalysis.md'
        ]
        
        for filename in enhanced_files:
            file_path = os.path.join(strategy_dir, filename)
            if os.path.exists(file_path):
                print(f"\nProcessing enhanced format file: {filename}")
                chunks_added = manager.process_strategy_document(file_path)
                print(f"Added {chunks_added} chunks from {filename}")
        
        # Then process any other .md files
        for filename in os.listdir(strategy_dir):
            if filename.endswith('.md') and filename not in enhanced_files and not filename.endswith('Sources.md'):
                file_path = os.path.join(strategy_dir, filename)
                print(f"\nProcessing file: {filename}")
                chunks_added = manager.process_strategy_document(file_path)
                print(f"Added {chunks_added} chunks from {filename}")
    
    # Test querying the database
    print("\n" + "="*50 + "\n")
    print("Testing database queries on the imported content:\n")
    
    test_queries = [
        "Israel Iran tensions Middle East",
        "AUKUS submarine deal",
        "China rare earth minerals",
        "Breaking events",
        "Strategic recommendations"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = query_db(query, n_results=2)
        for i, result in enumerate(results):
            preview = result[:150] + '...' if len(result) > 150 else result
            print(f"  Result {i+1}: {preview}")
