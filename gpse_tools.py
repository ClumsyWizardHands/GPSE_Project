"""
GPSE Tools Module
Collection of utility functions and tools for the GPSE project.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# CrewAI and ChromaDB imports
from crewai.tools import tool
import chromadb
from sentence_transformers import SentenceTransformer
from tavily import TavilyClient
from bs4 import BeautifulSoup
import requests as web_requests


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GPSETools:
    """Main tools class for GPSE project utilities."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.strategy_dir = self.project_root / "strategy_analyses"
        self.db_dir = self.project_root / "strategy_db_chroma"
        
    # File Operations
    def ensure_directory(self, directory: Path) -> None:
        """Ensure a directory exists, create if it doesn't."""
        directory = Path(directory)
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def read_json_file(self, filepath: Path) -> Dict[str, Any]:
        """Read and parse a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {filepath}: {e}")
            return {}
    
    def write_json_file(self, filepath: Path, data: Dict[str, Any], indent: int = 2) -> bool:
        """Write data to a JSON file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            logger.info(f"Successfully wrote to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error writing to {filepath}: {e}")
            return False
    
    # Strategy Analysis Tools
    def list_strategy_files(self) -> List[Path]:
        """List all strategy analysis files."""
        if not self.strategy_dir.exists():
            return []
        
        return list(self.strategy_dir.glob("*.md"))
    
    def parse_strategy_filename(self, filename: str) -> Dict[str, str]:
        """
        Parse strategy filename to extract components.
        Expected format: STRATEGY-MMDDYY-Description.md
        """
        parts = filename.replace('.md', '').split('-')
        if len(parts) >= 3:
            return {
                'strategy': parts[0],
                'date': parts[1],
                'description': '-'.join(parts[2:])
            }
        return {'raw': filename}
    
    # Date and Time Utilities
    def get_timestamp(self, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Get current timestamp in specified format."""
        return datetime.now().strftime(format_str)
    
    def get_date_code(self) -> str:
        """Get date code in MMDDYY format."""
        return datetime.now().strftime("%m%d%y")
    
    # Text Processing
    def truncate_text(self, text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Truncate text to specified length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    def clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and normalizing line breaks."""
        # Replace multiple spaces with single space
        text = ' '.join(text.split())
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        # Remove leading/trailing whitespace
        return text.strip()
    
    # Validation Utilities
    def validate_strategy_code(self, code: str) -> bool:
        """Validate strategy code format."""
        # Add validation logic based on your requirements
        if not code:
            return False
        # Example: Check if it's alphanumeric and 4 characters
        return code.isalnum() and len(code) == 4
    
    # Environment Utilities
    def get_env_variable(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Safely get environment variable."""
        return os.environ.get(key, default)
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        env = self.get_env_variable('ENVIRONMENT', 'development')
        return env.lower() == 'production'


# CrewAI Tool Functions
# These are decorated functions that become tools for agent use

@tool("Strategy Database Query")
def query_strategy_database(query_text: str) -> str:
    """
    Search the strategy database for relevant historical analyses and context.
    Provide a natural language query to find similar strategic insights,
    geopolitical analyses, or specific country/region information from past entries.
    """
    try:
        # Initialize persistent ChromaDB client
        client = chromadb.PersistentClient(path='./strategy_db_chroma')
        
        # Get collection
        try:
            collection = client.get_collection(name='grand_strategy')
        except Exception:
            return f"Database collection 'grand_strategy' not found. No historical analyses available yet."
        
        # Get the sentence transformer model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create embedding for the query
        logger.info(f"Creating embedding for query: {query_text[:50]}...")
        query_embedding = model.encode(query_text).tolist()
        
        # Query the collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        # Format and return the results
        if results and 'documents' in results and results['documents']:
            documents = results['documents'][0]  # Results are nested in a list
            
            if not documents:
                return "No matching historical analyses found for this query."
            
            # Format the results nicely
            formatted_results = []
            formatted_results.append(f"Found {len(documents)} relevant historical analyses:\n")
            
            for i, doc in enumerate(documents, 1):
                # Truncate very long documents for readability
                preview = doc[:500] + "..." if len(doc) > 500 else doc
                formatted_results.append(f"\n--- Result {i} ---")
                formatted_results.append(preview)
            
            return "\n".join(formatted_results)
        else:
            return "No matching historical analyses found for this query."
            
    except Exception as e:
        logger.error(f"Error querying database: {str(e)}")
        return f"Error searching the strategy database: {str(e)}"


@tool("Strategy Database Update")
def update_strategy_database(content_and_id: str) -> str:
    """
    Add new strategic analysis content to the database for future reference.
    Provide the text content and document ID separated by '|||'
    (e.g., 'content text|||DOC-ID-123').
    """
    try:
        # Parse the input to extract content and ID
        if '|||' not in content_and_id:
            return "Error: Input must be in format 'content|||document_id'"
        
        parts = content_and_id.split('|||', 1)
        text_content = parts[0].strip()
        document_id = parts[1].strip() if len(parts) > 1 else ""
        
        if not text_content or not document_id:
            return "Error: Both content and document ID are required"
        
        # Initialize persistent ChromaDB client
        client = chromadb.PersistentClient(path='./strategy_db_chroma')
        
        # Get or create collection
        collection = client.get_or_create_collection(name='grand_strategy')
        
        # Get the sentence transformer model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
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
        
        logger.info(f"Successfully added document {document_id} to collection grand_strategy")
        return f"Successfully added document '{document_id}' to the strategy database."
        
    except Exception as e:
        logger.error(f"Error adding text to database: {str(e)}")
        return f"Error adding document to the strategy database: {str(e)}"


@tool("Recent News Search")
def search_recent_news(query: str) -> str:
    """
    Search for recent news articles and current events related to geopolitics.
    Provide a query to find relevant news stories, political developments,
    and international affairs from the past few days.
    """
    try:
        # Get API key
        api_key = os.environ.get('TAVILY_API_KEY')
        if not api_key:
            return "Error: TAVILY_API_KEY not found in environment variables"
        
        client = TavilyClient(api_key=api_key)
        
        # Calculate date range for recent news
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Prepare search parameters
        search_params = {
            "query": query,
            "max_results": 5,
            "search_depth": "advanced",
            "topic": "news",
            "include_domains": [],
            "exclude_domains": []
        }
        
        # Add date filtering to query
        date_query = f"{query} after:{start_date.strftime('%Y-%m-%d')}"
        search_params["query"] = date_query
        
        logger.info(f"Searching for news: {query} (last 7 days)")
        
        # Perform the search
        results = client.search(**search_params)
        
        # Format the results
        if not results or 'results' not in results:
            return "No news articles found for the given query."
        
        news_items = results['results']
        if not news_items:
            return "No news articles found for the given query."
        
        # Format the results nicely
        formatted_results = []
        formatted_results.append(f"Found {len(news_items)} recent news articles:\n")
        
        for i, item in enumerate(news_items, 1):
            formatted_results.append(f"\n--- Article {i} ---")
            formatted_results.append(f"Title: {item.get('title', 'No title')}")
            formatted_results.append(f"URL: {item.get('url', 'No URL')}")
            
            # Add published date if available
            if 'published_date' in item:
                formatted_results.append(f"Published: {item['published_date']}")
            
            # Add snippet/content preview
            content = item.get('content', item.get('snippet', 'No content available'))
            if content:
                # Truncate long content
                preview = content[:300] + "..." if len(content) > 300 else content
                formatted_results.append(f"Summary: {preview}")
            
            # Add relevance score if available
            if 'score' in item:
                formatted_results.append(f"Relevance: {item['score']:.2f}")
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"Error searching news with Tavily: {str(e)}")
        return f"Error searching for news: {str(e)}"


@tool("Simple Web Scraper")
def scrape_web_page(url: str) -> str:
    """
    Scrape text content from a web page. Provide a URL to fetch the page
    and extract the main text content, particularly from paragraph tags
    and other text elements. Useful for gathering information from web sources.
    """
    try:
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            return f"Invalid URL format. URL must start with http:// or https://. Received: {url}"
        
        logger.info(f"Fetching web page: {url}")
        
        # Set headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make the HTTP request
        response = web_requests.get(url, headers=headers, timeout=10)
        
        # Check for successful response
        if response.status_code != 200:
            return f"Failed to fetch page. HTTP status code: {response.status_code}"
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Extract text from different elements
        text_elements = []
        
        # Get title
        title = soup.find('title')
        if title:
            text_elements.append(f"Title: {title.get_text(strip=True)}")
            text_elements.append("\n" + "="*50 + "\n")
        
        # Get main content - try different strategies
        
        # Strategy 1: Look for main content containers
        main_containers = soup.find_all(['main', 'article', 'div'], 
                                      attrs={'class': ['content', 'main-content', 'article-body', 'entry-content']})
        
        if main_containers:
            for container in main_containers:
                paragraphs = container.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:  # Filter out very short paragraphs
                        text_elements.append(text)
        else:
            # Strategy 2: Get all paragraphs if no main container found
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 20:  # Filter out very short paragraphs
                    text_elements.append(text)
        
        # Also get important headings
        headings = soup.find_all(['h1', 'h2', 'h3'])
        for heading in headings:
            h_text = heading.get_text(strip=True)
            if h_text:
                text_elements.append(f"\n### {h_text}\n")
                # Get the next few paragraphs after each heading
                next_sibling = heading.find_next_sibling()
                while next_sibling and next_sibling.name == 'p':
                    p_text = next_sibling.get_text(strip=True)
                    if p_text and len(p_text) > 20:
                        text_elements.append(p_text)
                    next_sibling = next_sibling.find_next_sibling()
                    if next_sibling and next_sibling.name in ['h1', 'h2', 'h3']:
                        break
        
        # Get list items if they contain substantial text
        lists = soup.find_all(['ul', 'ol'])
        for lst in lists:
            items = lst.find_all('li')
            list_text = []
            for item in items:
                item_text = item.get_text(strip=True)
                if item_text and len(item_text) > 10:
                    list_text.append(f"• {item_text}")
            if list_text:
                text_elements.extend(list_text)
        
        # Combine all text elements
        if text_elements:
            full_text = "\n\n".join(text_elements)
            
            # Clean up excessive newlines
            full_text = "\n".join(line for line in full_text.split("\n") if line.strip())
            
            # Truncate if too long
            if len(full_text) > 5000:
                full_text = full_text[:5000] + "\n\n[Content truncated due to length...]"
            
            return f"Successfully scraped content from {url}:\n\n{full_text}"
        else:
            return f"No text content found on the page at {url}. The page might be empty, use JavaScript rendering, or have an unusual structure."
            
    except web_requests.exceptions.Timeout:
        logger.error(f"Timeout while fetching URL: {url}")
        return f"Request timed out after 10 seconds while fetching {url}"
        
    except web_requests.exceptions.ConnectionError:
        logger.error(f"Connection error while fetching URL: {url}")
        return f"Connection error: Unable to reach {url}. Please check if the URL is correct and the server is accessible."
        
    except web_requests.exceptions.RequestException as e:
        logger.error(f"Request error while fetching URL {url}: {str(e)}")
        return f"Error fetching the web page: {str(e)}"
        
    except Exception as e:
        logger.error(f"Unexpected error while scraping {url}: {str(e)}")
        return f"Unexpected error while scraping the web page: {str(e)}"


# Create wrapper classes for consistent interface
class StrategyDBQueryTool:
    """Wrapper class for strategy database query tool."""
    def __init__(self):
        self.tool = query_strategy_database


class StrategyDBUpdateTool:
    """Wrapper class for strategy database update tool."""
    def __init__(self):
        self.tool = update_strategy_database


class TavilyNewsSearchTool:
    """Wrapper class for Tavily news search tool."""
    def __init__(self):
        self.tool = search_recent_news


class SimpleWebScraperTool:
    """Wrapper class for web scraper tool."""
    def __init__(self):
        self.tool = scrape_web_page


# Convenience functions
_tools = None

def get_tools() -> GPSETools:
    """Get singleton instance of GPSETools."""
    global _tools
    if _tools is None:
        _tools = GPSETools()
    return _tools


# Export commonly used functions at module level
def ensure_directory(directory: Path) -> None:
    """Ensure a directory exists."""
    return get_tools().ensure_directory(directory)


def get_timestamp(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Get current timestamp."""
    return get_tools().get_timestamp(format_str)


def get_date_code() -> str:
    """Get date code in MMDDYY format."""
    return get_tools().get_date_code()


def list_strategy_files() -> List[Path]:
    """List all strategy analysis files."""
    return get_tools().list_strategy_files()


if __name__ == "__main__":
    # Example usage
    tools = GPSETools()
    
    print(f"Project root: {tools.project_root}")
    print(f"Current timestamp: {tools.get_timestamp()}")
    print(f"Date code: {tools.get_date_code()}")
    
    # List strategy files
    strategies = tools.list_strategy_files()
    print(f"\nFound {len(strategies)} strategy files:")
    for strategy in strategies:
        parsed = tools.parse_strategy_filename(strategy.name)
        print(f"  - {strategy.name}: {parsed}")
    
    # Test the tools
    print("\n" + "="*50)
    print("Testing Database Query Tool:")
    print("="*50 + "\n")
    
    # Test query
    result = query_strategy_database("What is China's current AI strategy?")
    print(result)
    
    # Test the other tools only if needed
    print("\nTools are ready for use with CrewAI agents!")
