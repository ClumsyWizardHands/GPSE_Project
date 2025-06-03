"""
GPSE Crew Implementation using CrewAI Best Practices
"""
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import yaml
import logging

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field

# Import our existing modules
from db_manager import ChromaDBManager

# Import additions to patch gpse_tools
import gpse_tools_additions

from gpse_tools import (
    save_strategy_document, 
    process_strategy_document,
    query_chromadb,
    get_date_code,
    setup_logging
)

# Setup logging
logger = setup_logging()

class NewsArticle(BaseModel):
    """Model for news article data"""
    url: str
    title: str
    date: str
    source: str
    summary: str
    relevance_score: float = Field(ge=0, le=1)
    credibility: float = Field(ge=0, le=1)

class AnalysisOutput(BaseModel):
    """Model for analysis output"""
    executive_summary: str
    primary_observations: List[Dict[str, Any]]
    scenario_implications: str
    articles_processed: int
    historical_matches: int

@CrewBase
class GPSECrew():
    """Geopolitical Grand Strategy Engine Crew"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self):
        """Initialize the crew with necessary components"""
        self.db_manager = ChromaDBManager()
        self._load_configs()
        self._setup_llms()
        
    def _load_configs(self):
        """Load YAML configurations"""
        try:
            with open(self.agents_config, 'r') as f:
                self.agents_yaml = yaml.safe_load(f)
            with open(self.tasks_config, 'r') as f:
                self.tasks_yaml = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load configuration files: {e}")
            raise
    
    def _setup_llms(self):
        """Setup LLM instances based on environment configuration"""
        # Check which API keys are available
        openai_key = os.getenv('OPENAI_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Setup efficient LLM (for news gathering and archival)
        if openai_key:
            self.efficient_llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.3,
                api_key=openai_key
            )
            logger.info("Using GPT-3.5-turbo for efficient tasks")
        else:
            raise ValueError("OpenAI API key required for efficient LLM")
        
        # Setup powerful LLM (for strategic analysis)
        if anthropic_key:
            self.powerful_llm = ChatAnthropic(
                model="claude-3-opus-20240229",
                temperature=0.5,
                api_key=anthropic_key
            )
            logger.info("Using Claude 3 Opus for strategic analysis")
        elif openai_key:
            self.powerful_llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=0.5,
                api_key=openai_key
            )
            logger.info("Using GPT-4 Turbo for strategic analysis")
        else:
            raise ValueError("Either Anthropic or OpenAI API key required for powerful LLM")
    
    @before_kickoff
    def prepare_analysis(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare for analysis run"""
        logger.info("=== GPSE Analysis Starting ===")
        
        # Add timestamp and date code
        inputs['timestamp'] = datetime.now()
        inputs['date_code'] = get_date_code()
        inputs['analysis_id'] = f"GGSM-{inputs['date_code']}"
        
        # Log current database state
        collection_size = len(self.db_manager.collection.get()['ids'])
        logger.info(f"ChromaDB collection size: {collection_size} documents")
        
        return inputs
    
    @after_kickoff
    def post_process(self, result):
        """Post-process results after crew execution"""
        logger.info("=== Post-processing results ===")
        
        try:
            # Find the output file
            output_files = [f for f in os.listdir('strategy_analyses') 
                          if f.startswith(f"GGSM-{get_date_code()}")]
            
            if output_files:
                latest_file = os.path.join('strategy_analyses', output_files[-1])
                logger.info(f"Processing document: {latest_file}")
                
                # Add to ChromaDB
                chunks_added = self.db_manager.process_strategy_document(latest_file)
                logger.info(f"Added {chunks_added} chunks to ChromaDB")
            else:
                logger.warning("No output file found for archival")
                
        except Exception as e:
            logger.error(f"Error in post-processing: {e}")
        
        logger.info("=== GPSE Analysis Complete ===")
        return result
    
    # Agent definitions
    @agent
    def news_scout(self) -> Agent:
        """News Scout Agent - Gathers recent geopolitical news"""
        return Agent(
            config=self.agents_yaml['news_scout'],
            tools=[
                TavilyNewsSearchTool(),
                NewsAPITool()
            ],
            llm=self.efficient_llm,
            max_iter=3,
            max_execution_time=300,  # 5 minutes max
            allow_delegation=False,
            verbose=True
        )
    
    @agent
    def info_curator(self) -> Agent:
        """Information Curator - Synthesizes and filters news"""
        return Agent(
            config=self.agents_yaml['info_curator'],
            tools=[ValidateSourcesTool()],
            llm=self.efficient_llm,
            max_iter=2,
            allow_delegation=False,
            verbose=True
        )
    
    @agent
    def strategy_analyst(self) -> Agent:
        """Lead Strategy Analyst - Performs deep analysis"""
        return Agent(
            config=self.agents_yaml['strategy_analyst'],
            tools=[
                ChromaDBQueryTool(self.db_manager),
                HistoricalPatternAnalyzer(self.db_manager)
            ],
            llm=self.powerful_llm,
            max_iter=3,
            allow_delegation=True,
            verbose=True
        )
    
    @agent
    def comms_archival(self) -> Agent:
        """Communications & Archival Lead - Formats and stores results"""
        return Agent(
            config=self.agents_yaml['comms_archival'],
            tools=[
                save_strategy_document,
                DocumentFormatterTool(),
                ChromaDBAddTool(self.db_manager)
            ],
            llm=self.efficient_llm,
            max_iter=2,
            allow_delegation=False,
            verbose=True
        )
    
    # Task definitions
    @task
    def news_scout_task(self) -> Task:
        """Task for gathering news"""
        return Task(
            config=self.tasks_yaml['news_scout_task'],
            output_pydantic=NewsArticle
        )
    
    @task
    def gather_news_task(self) -> Task:
        """Task for curating and synthesizing news"""
        return Task(
            config=self.tasks_yaml['gather_news_task']
        )
    
    @task
    def analyze_strategy_task(self) -> Task:
        """Task for strategic analysis"""
        return Task(
            config=self.tasks_yaml['analyze_strategy_task'],
            output_pydantic=AnalysisOutput
        )
    
    @task
    def document_archive_task(self) -> Task:
        """Task for documentation and archival"""
        return Task(
            config=self.tasks_yaml['document_archive_task']
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the GPSE crew"""
        return Crew(
            agents=self.agents,  # Automatically created by @agent decorator
            tasks=self.tasks,    # Automatically created by @task decorator
            process=Process.sequential,
            memory=True,         # Enable memory for better context
            verbose=True,
            max_rpm=10,         # Rate limiting
            share_crew=False
        )

# Tool Implementations with Error Handling and Retry Logic

class ResilientTool(BaseTool):
    """Base class for tools with retry logic"""
    
    def _run_with_retry(self, func, *args, **kwargs):
        """Execute function with exponential backoff retry"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"All retry attempts failed: {e}")
                    raise
                wait_time = 2 ** attempt
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                import time
                time.sleep(wait_time)

class TavilyNewsSearchTool(ResilientTool):
    name: str = "Tavily News Search"
    description: str = "Search for recent news using Tavily AI-optimized search"
    
    def _run(self, query: str) -> str:
        """Run Tavily search with retry logic"""
        def search():
            # Import here to avoid issues if not installed
            from tavily import TavilyClient
            
            client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
            results = client.search(
                query=query,
                search_depth="advanced",
                max_results=10,
                include_domains=[],
                exclude_domains=[]
            )
            
            # Format results
            articles = []
            for r in results.get('results', []):
                articles.append({
                    'url': r.get('url'),
                    'title': r.get('title'),
                    'content': r.get('content'),
                    'score': r.get('score', 0.5)
                })
            
            return str(articles)
        
        return self._run_with_retry(search)

class NewsAPITool(ResilientTool):
    name: str = "News API Search"
    description: str = "Search for news articles using NewsAPI"
    
    def _run(self, query: str) -> str:
        """Run NewsAPI search with retry logic"""
        def search():
            import requests
            
            api_key = os.getenv('NEWS_API_KEY')
            if not api_key:
                return "NewsAPI key not configured"
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'apiKey': api_key,
                'sortBy': 'relevancy',
                'pageSize': 20,
                'language': 'en'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for article in data.get('articles', []):
                articles.append({
                    'url': article.get('url'),
                    'title': article.get('title'),
                    'source': article.get('source', {}).get('name'),
                    'date': article.get('publishedAt'),
                    'description': article.get('description')
                })
            
            return str(articles)
        
        return self._run_with_retry(search)

class ValidateSourcesTool(BaseTool):
    name: str = "Validate News Sources"
    description: str = "Validate credibility and relevance of news sources"
    
    def _run(self, sources: str) -> str:
        """Validate news sources for credibility"""
        # Simple validation logic - can be enhanced
        validated = []
        try:
            import json
            sources_list = json.loads(sources) if isinstance(sources, str) else sources
            
            for source in sources_list:
                credibility = 0.8  # Default score
                
                # Enhance credibility scoring based on source
                trusted_sources = ['reuters', 'ap', 'bbc', 'cnn', 'nytimes', 'wsj']
                source_name = source.get('source', '').lower()
                
                if any(trusted in source_name for trusted in trusted_sources):
                    credibility = 0.95
                
                source['credibility'] = credibility
                if credibility >= 0.7:
                    validated.append(source)
            
            return str(validated)
        except Exception as e:
            logger.error(f"Error validating sources: {e}")
            return sources

class ChromaDBQueryTool(BaseTool):
    name: str = "Query Historical Analyses"
    description: str = "Query ChromaDB for relevant historical analyses"
    
    def __init__(self, db_manager: ChromaDBManager):
        super().__init__()
        self.db_manager = db_manager
    
    def _run(self, query: str, n_results: int = 5) -> str:
        """Query ChromaDB for historical context"""
        try:
            results = self.db_manager.query_db(query, n_results)
            
            # Format results for agent consumption
            formatted = []
            for i, (doc, meta, dist) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                formatted.append({
                    'relevance_rank': i + 1,
                    'distance': dist,
                    'document_id': meta.get('document_id'),
                    'section': meta.get('section'),
                    'date': meta.get('date'),
                    'content': doc[:500] + "..." if len(doc) > 500 else doc
                })
            
            return str(formatted)
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return "No historical context available"

class HistoricalPatternAnalyzer(BaseTool):
    name: str = "Analyze Historical Patterns"
    description: str = "Analyze patterns from historical strategic analyses"
    
    def __init__(self, db_manager: ChromaDBManager):
        super().__init__()
        self.db_manager = db_manager
    
    def _run(self, topic: str) -> str:
        """Analyze historical patterns related to a topic"""
        try:
            # Query for related historical analyses
            results = self.db_manager.query_db(topic, n_results=10)
            
            # Extract patterns (simplified version)
            patterns = {
                'recurring_themes': [],
                'escalation_patterns': [],
                'actor_behaviors': {}
            }
            
            # Analyze documents for patterns
            for doc in results['documents'][0]:
                # Simple pattern extraction - can be enhanced
                if 'escalation' in doc.lower():
                    patterns['escalation_patterns'].append("Escalation pattern detected")
                if 'china' in doc.lower():
                    patterns['actor_behaviors']['China'] = "Strategic behavior noted"
                # Add more sophisticated pattern recognition
            
            return str(patterns)
        except Exception as e:
            logger.error(f"Error analyzing patterns: {e}")
            return "Pattern analysis unavailable"

class DocumentFormatterTool(BaseTool):
    name: str = "Format Strategic Document"
    description: str = "Format analysis into GPSE standard document structure"
    
    def _run(self, content: str, metadata: dict = None) -> str:
        """Format content into standard GPSE document structure"""
        try:
            date_str = datetime.now().strftime("%B %d, %Y")
            date_code = get_date_code()
            
            formatted = f"""---
## Geopolitical Grand Strategy Monitor
**Strategic Synthesis Entry**
**Date:** {date_str}
**Entry ID:** GGSM-{date_code}-DailyAnalysis

{content}
---"""
            
            return formatted
        except Exception as e:
            logger.error(f"Error formatting document: {e}")
            return content

class ChromaDBAddTool(BaseTool):
    name: str = "Add to ChromaDB"
    description: str = "Add processed document to ChromaDB"
    
    def __init__(self, db_manager: ChromaDBManager):
        super().__init__()
        self.db_manager = db_manager
    
    def _run(self, document_path: str) -> str:
        """Add document to ChromaDB"""
        try:
            chunks_added = self.db_manager.process_strategy_document(document_path)
            return f"Successfully added {chunks_added} chunks to ChromaDB"
        except Exception as e:
            logger.error(f"Error adding to ChromaDB: {e}")
            return f"Failed to add document: {str(e)}"

# Main execution
def main():
    """Main execution function"""
    try:
        # Initialize crew
        gpse_crew = GPSECrew()
        
        # Prepare inputs
        inputs = {
            'topic': 'global geopolitical developments',
            'focus_areas': [
                'Ukraine-Russia conflict',
                'Middle East tensions',
                'US-China relations',
                'Indo-Pacific dynamics'
            ]
        }
        
        # Execute crew
        result = gpse_crew.crew().kickoff(inputs=inputs)
        
        logger.info(f"Analysis complete. Result: {result}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()
