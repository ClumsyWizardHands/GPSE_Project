"""
Additional functions for GPSE tools that are imported by gpse_crew.py
"""
import logging
from pathlib import Path
from datetime import datetime
from crewai.tools import tool

# Import the main tools module
from gpse_tools import get_tools, query_strategy_database, logger


def setup_logging(name: str = None):
    """Setup logging with standardized format."""
    logger_instance = logging.getLogger(name or __name__)
    if not logger_instance.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger_instance.addHandler(handler)
        logger_instance.setLevel(logging.INFO)
    return logger_instance


@tool("Save Strategy Document")
def save_strategy_document(content: str, filename: str = None) -> str:
    """
    Save strategic analysis content to a markdown file in the strategy_analyses directory.
    If no filename is provided, generates one based on current date.
    """
    try:
        tools = get_tools()
        
        # Ensure strategy directory exists
        tools.ensure_directory(tools.strategy_dir)
        
        # Generate filename if not provided
        if not filename:
            date_code = tools.get_date_code()
            timestamp = tools.get_timestamp("%H%M%S")
            filename = f"GGSM-{date_code}-Analysis_{timestamp}.md"
        
        # Ensure .md extension
        if not filename.endswith('.md'):
            filename += '.md'
        
        # Full path
        filepath = tools.strategy_dir / filename
        
        # Write the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Successfully saved strategy document to {filepath}")
        return f"Successfully saved strategy document to {filename}"
        
    except Exception as e:
        logger.error(f"Error saving strategy document: {str(e)}")
        return f"Error saving strategy document: {str(e)}"


def process_strategy_document(filepath: str) -> int:
    """
    Process a strategy document and add it to ChromaDB.
    This is a wrapper for the ChromaDBManager functionality.
    """
    try:
        from db_manager import ChromaDBManager
        
        db_manager = ChromaDBManager()
        chunks_added = db_manager.process_strategy_document(filepath)
        
        logger.info(f"Processed strategy document {filepath}, added {chunks_added} chunks")
        return chunks_added
        
    except Exception as e:
        logger.error(f"Error processing strategy document: {str(e)}")
        return 0


@tool("Query ChromaDB")
def query_chromadb(query: str, n_results: int = 5) -> str:
    """
    Query ChromaDB for relevant historical analyses.
    This is an alias for query_strategy_database with a different interface.
    """
    return query_strategy_database(query)


# Now add these to the original gpse_tools module
import sys
import gpse_tools

# Add the new functions to the gpse_tools module
gpse_tools.setup_logging = setup_logging
gpse_tools.save_strategy_document = save_strategy_document
gpse_tools.process_strategy_document = process_strategy_document
gpse_tools.query_chromadb = query_chromadb

# Also make them available at module level
sys.modules['gpse_tools'].setup_logging = setup_logging
sys.modules['gpse_tools'].save_strategy_document = save_strategy_document
sys.modules['gpse_tools'].process_strategy_document = process_strategy_document
sys.modules['gpse_tools'].query_chromadb = query_chromadb
