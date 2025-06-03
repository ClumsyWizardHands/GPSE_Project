"""
Extended GPSE Crew Implementation with Geo Analyst
"""
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import yaml
import logging

from crewai import Agent, Crew, Process, Task
from crewai.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field

# Import our existing modules
from db_manager import ChromaDBManager
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

# Global DB manager for tools
_global_db_manager = None

def set_global_db_manager(db_manager):
    global _global_db_manager
    _global_db_manager = db_manager

def get_global_db_manager():
    return _global_db_manager

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

class GPSECrew:
    """Extended Geopolitical Grand Strategy Engine Crew with Geo Analyst"""
    
    def __init__(self):
        """Initialize the crew with necessary components"""
        self.db_manager = ChromaDBManager()
        set_global_db_manager(self.db_manager)  # Set global for tools
        self._load_configs()
        self._setup_llms()
        self._create_agents()
        self._create_tasks()
        
    def _load_configs(self):
        """Load YAML configurations"""
        try:
            with open('config/agents.yaml', 'r') as f:
                self.agents_yaml = yaml.safe_load(f)
            with open('config/tasks.yaml', 'r') as f:
                self.tasks_yaml = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load configuration files: {e}")
            raise
    
    def _setup_llms(self):
        """Setup LLM instances based on environment configuration"""
        openai_key = os.getenv('OPENAI_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        if openai_key:
            self.efficient_llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.3,
                api_key=openai_key
            )
            logger.info("Using GPT-3.5-turbo for efficient tasks")
        else:
            raise ValueError("OpenAI API key required for efficient LLM")
        
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
    
    def _create_agents(self):
        """Create all agents"""
        # News Scout
        news_config = self.agents_yaml['news_scout']
        self.news_scout = Agent(
            role=news_config['role'],
            goal=news_config['goal'],
            backstory=news_config['backstory'],
            tools=[
                TavilyNewsSearchTool(),
                NewsAPITool()
            ],
            llm=self.efficient_llm,
            max_iter=3,
            allow_delegation=False,
            verbose=True
        )
        
        # Info Curator
        info_config = self.agents_yaml['info_curator']
        self.info_curator = Agent(
            role=info_config['role'],
            goal=info_config['goal'],
            backstory=info_config['backstory'],
            tools=[ValidateSourcesTool()],
            llm=self.efficient_llm,
            max_iter=2,
            allow_delegation=False,
            verbose=True
        )
        
        # Strategy Analyst
        strategy_config = self.agents_yaml['strategy_analyst']
        self.strategy_analyst = Agent(
            role=strategy_config['role'],
            goal=strategy_config['goal'],
            backstory=strategy_config['backstory'],
            tools=[
                ChromaDBQueryTool(),
                HistoricalPatternAnalyzer()
            ],
            llm=self.powerful_llm,
            max_iter=3,
            allow_delegation=True,
            verbose=True
        )
        
        # Comms Archival
        comms_config = self.agents_yaml['comms_archival']
        self.comms_archival = Agent(
            role=comms_config['role'],
            goal=comms_config['goal'],
            backstory=comms_config['backstory'],
            tools=[
                save_strategy_document,
                DocumentFormatterTool(),
                ChromaDBAddTool()
            ],
            llm=self.efficient_llm,
            max_iter=2,
            allow_delegation=False,
            verbose=True
        )
        
        # Geo Analyst - NEW
        geo_config = self.agents_yaml['geo_analyst']
        self.geo_analyst = Agent(
            role=geo_config['role'],
            goal=geo_config['goal'],
            backstory=geo_config['backstory'],
            tools=[
                StrategyDBQueryTool(),
                ChromaDBQueryTool(),
                HistoricalPatternAnalyzer()
            ],
            llm=self.powerful_llm,  # Uses Claude 4 Opus as configured
            max_iter=5,  # Allow more iterations for comprehensive analysis
            allow_delegation=True,
            verbose=True
        )
    
    def _create_tasks(self):
        """Create all tasks"""
        # News Scout Task
        news_task_config = self.tasks_yaml['news_scout_task']
        self.news_scout_task = Task(
            description=news_task_config['description'],
            expected_output=news_task_config['expected_output'],
            agent=self.news_scout
        )
        
        # Gather News Task
        gather_task_config = self.tasks_yaml['gather_news_task']
        self.gather_news_task = Task(
            description=gather_task_config['description'],
            expected_output=gather_task_config['expected_output'],
            agent=self.info_curator,
            context=[self.news_scout_task]
        )
        
        # Analyze Strategy Task
        analyze_task_config = self.tasks_yaml['analyze_strategy_task']
        self.analyze_strategy_task = Task(
            description=analyze_task_config['description'],
            expected_output=analyze_task_config['expected_output'],
            agent=self.strategy_analyst,
            context=[self.gather_news_task]
        )
        
        # Geo Analyst Task - NEW
        geo_task_config = self.tasks_yaml['geo_analyst_task']
        self.geo_analyst_task = Task(
            description=geo_task_config['description'],
            expected_output=geo_task_config['expected_output'],
            agent=self.geo_analyst,
            context=[self.gather_news_task, self.analyze_strategy_task]
        )
        
        # Document Archive Task
        archive_task_config = self.tasks_yaml['document_archive_task']
        output_file = archive_task_config.get('output_file', '')
        if '{date_code}' in output_file:
            output_file = output_file.replace('{date_code}', get_date_code())
        
        self.document_archive_task = Task(
            description=archive_task_config['description'],
            expected_output=archive_task_config['expected_output'],
            agent=self.comms_archival,
            context=[self.analyze_strategy_task, self.geo_analyst_task],
            output_file=output_file if output_file else None
        )
    
    def create_crew(self) -> Crew:
        """Create and return the crew"""
        return Crew(
            agents=[
                self.news_scout,
                self.info_curator,
                self.strategy_analyst,
                self.geo_analyst,  # Added geo_analyst
                self.comms_archival
            ],
            tasks=[
                self.news_scout_task,
                self.gather_news_task,
                self.analyze_strategy_task,
                self.geo_analyst_task,  # Added geo_analyst_task
                self.document_archive_task
            ],
            process=Process.sequential,
            memory=True,
            verbose=True,
            max_rpm=10
        )

# Tool Implementations
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
            from tavily import TavilyClient
            
            client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
            results = client.search(
                query=query,
                search_depth="advanced",
                max_results=10,
                include_domains=[],
                exclude_domains=[]
            )
            
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
        validated = []
        try:
            import json
            sources_list = json.loads(sources) if isinstance(sources, str) else sources
            
            for source in sources_list:
                credibility = 0.8
                
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
    
    def _run(self, query: str, n_results: int = 5) -> str:
        """Query ChromaDB for historical context"""
        try:
            db_manager = get_global_db_manager()
            if not db_manager:
                return "Database not initialized"
                
            results = db_manager.query_db(query, n_results)
            
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
    
    def _run(self, topic: str) -> str:
        """Analyze historical patterns related to a topic"""
        try:
            db_manager = get_global_db_manager()
            if not db_manager:
                return "Database not initialized"
                
            results = db_manager.query_db(topic, n_results=10)
            
            patterns = {
                'recurring_themes': [],
                'escalation_patterns': [],
                'actor_behaviors': {}
            }
            
            for doc in results['documents'][0]:
                if 'escalation' in doc.lower():
                    patterns['escalation_patterns'].append("Escalation pattern detected")
                if 'china' in doc.lower():
                    patterns['actor_behaviors']['China'] = "Strategic behavior noted"
            
            return str(patterns)
        except Exception as e:
            logger.error(f"Error analyzing patterns: {e}")
            return "Pattern analysis unavailable"

class StrategyDBQueryTool(BaseTool):
    """
    Tool for geo_analyst to query ChromaDB for historical grand strategy documents.
    Provides enhanced querying with structured output optimized for strategic analysis.
    """
    name: str = "Strategy Database Query"
    description: str = "Query historical grand strategy documents with enhanced context for geopolitical analysis"
    
    def _run(self, query: str, n_results: int = 10) -> str:
        """
        Execute strategic query with metadata-enriched results
        """
        try:
            db_manager = get_global_db_manager()
            if not db_manager:
                return "Strategy database not initialized"
            
            # Perform the query
            results = db_manager.query_db(query, n_results)
            
            # Structure results with strategic metadata
            strategic_results = {
                "[Query]": query,
                "[Total_Matches]": len(results['documents'][0]) if results['documents'] else 0,
                "[Historical_Context]": []
            }
            
            if results['documents'] and results['documents'][0]:
                for i, (doc, meta, dist) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    context_entry = {
                        "[Relevance_Score]": 1 - dist,  # Convert distance to similarity
                        "[Document_ID]": meta.get('document_id', 'Unknown'),
                        "[Date]": meta.get('date', 'Unknown'),
                        "[Section]": meta.get('section', 'Unknown'),
                        "[Actors]": self._extract_actors(doc),
                        "[Strategic_Content]": doc[:1000],  # More content for analysis
                        "[Inferred_Ends]": self._infer_strategic_ends(doc),
                        "[Means]": self._extract_means(doc),
                        "[Alignment_Signals]": self._detect_alignments(doc),
                        "[Flashpoints]": self._identify_flashpoints(doc),
                        "[Scenario_Potential]": self._assess_scenarios(doc)
                    }
                    strategic_results["[Historical_Context]"].append(context_entry)
            
            return str(strategic_results)
            
        except Exception as e:
            logger.error(f"Strategic query error: {e}")
            return f"Strategy database query failed: {str(e)}"
    
    def _extract_actors(self, text: str) -> List[str]:
        """Extract key actors mentioned in the text"""
        actors = []
        key_actors = ['United States', 'China', 'Russia', 'NATO', 'EU', 'India', 
                      'Iran', 'Israel', 'Ukraine', 'Taiwan', 'North Korea', 'Japan']
        
        for actor in key_actors:
            if actor.lower() in text.lower():
                actors.append(actor)
        
        return actors
    
    def _infer_strategic_ends(self, text: str) -> List[str]:
        """Infer strategic objectives from text"""
        ends = []
        end_keywords = {
            'hegemony': 'Hegemonic dominance',
            'deterrence': 'Strategic deterrence',
            'alliance': 'Alliance building',
            'containment': 'Containment strategy',
            'expansion': 'Territorial/influence expansion',
            'security': 'Security maximization'
        }
        
        for keyword, end in end_keywords.items():
            if keyword in text.lower():
                ends.append(end)
        
        return ends
    
    def _extract_means(self, text: str) -> List[str]:
        """Extract strategic means/methods"""
        means = []
        means_keywords = {
            'military': 'Military force projection',
            'sanction': 'Economic sanctions',
            'diplomatic': 'Diplomatic engagement',
            'cyber': 'Cyber operations',
            'proxy': 'Proxy warfare',
            'nuclear': 'Nuclear capability'
        }
        
        for keyword, mean in means_keywords.items():
            if keyword in text.lower():
                means.append(mean)
        
        return means
    
    def _detect_alignments(self, text: str) -> List[str]:
        """Detect alignment signals between actors"""
        alignments = []
        alignment_patterns = {
            'cooperation': 'Cooperative alignment',
            'partnership': 'Strategic partnership',
            'opposition': 'Adversarial alignment',
            'neutral': 'Neutral positioning',
            'support': 'Support alignment'
        }
        
        for pattern, alignment in alignment_patterns.items():
            if pattern in text.lower():
                alignments.append(alignment)
        
        return alignments
    
    def _identify_flashpoints(self, text: str) -> List[str]:
        """Identify potential flashpoints"""
        flashpoints = []
        flashpoint_keywords = ['taiwan', 'ukraine', 'baltic', 'south china sea', 
                               'kashmir', 'iran nuclear', 'korean peninsula']
        
        for keyword in flashpoint_keywords:
            if keyword in text.lower():
                flashpoints.append(keyword.title())
        
        return flashpoints
    
    def _assess_scenarios(self, text: str) -> str:
        """Assess scenario potential based on content"""
        escalation_keywords = ['escalation', 'conflict', 'tension', 'crisis', 'war']
        de_escalation_keywords = ['dialogue', 'negotiation', 'agreement', 'peace', 'cooperation']
        
        escalation_count = sum(1 for keyword in escalation_keywords if keyword in text.lower())
        de_escalation_count = sum(1 for keyword in de_escalation_keywords if keyword in text.lower())
        
        if escalation_count > de_escalation_count:
            return "High escalation potential"
        elif de_escalation_count > escalation_count:
            return "De-escalation trajectory"
        else:
            return "Stable/uncertain trajectory"

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
    
    def _run(self, document_path: str) -> str:
        """Add document to ChromaDB"""
        try:
            db_manager = get_global_db_manager()
            if not db_manager:
                return "Database not initialized"
                
            chunks_added = db_manager.process_strategy_document(document_path)
            return f"Successfully added {chunks_added} chunks to ChromaDB"
        except Exception as e:
            logger.error(f"Error adding to ChromaDB: {e}")
            return f"Failed to add document: {str(e)}"

# Main execution
def main():
    """Main execution function"""
    try:
        logger.info("=== Starting GPSE Crew with Geo Analyst ===")
        
        # Initialize crew
        gpse_crew = GPSECrew()
        crew = gpse_crew.create_crew()
        
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
        
        # Log database state
        collection_size = len(gpse_crew.db_manager.collection.get()['ids'])
        logger.info(f"ChromaDB collection size: {collection_size} documents")
        
        # Execute crew
        result = crew.kickoff(inputs=inputs)
        
        logger.info(f"Analysis complete. Result: {result}")
        
        # Post-process - add to ChromaDB
        try:
            output_files = [f for f in os.listdir('strategy_analyses') 
                          if f.startswith(f"GGSM-{get_date_code()}")]
            
            if output_files:
                latest_file = os.path.join('strategy_analyses', output_files[-1])
                logger.info(f"Processing document: {latest_file}")
                chunks_added = gpse_crew.db_manager.process_strategy_document(latest_file)
                logger.info(f"Added {chunks_added} chunks to ChromaDB")
            else:
                logger.warning("No output file found for archival")
        except Exception as e:
            logger.error(f"Error in post-processing: {e}")
        
        logger.info("=== GPSE Analysis Complete ===")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()
