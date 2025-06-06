"""
GPSE Main Crew - Clean Version
Removes custom ChromaDB configurations and uses CrewAI defaults
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# CrewAI imports
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff

# LangChain imports for LLM initialization
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Import custom tools
from gpse_tools import (
    query_strategy_database,
    get_date_code,
    get_timestamp,
    ensure_directory
)

# Import enhanced news tools
from gpse_tools import (
    enhanced_news_search,
    fetch_news_from_url,
    aggregate_geopolitical_news
)

# Import communicator tools
from communicator_agent_implementation import (
    FileWriterTool,
    StrategyDBUpdateTool as CommunicatorDBUpdateTool,
    create_communicator_agent
)

# Load environment variables
load_dotenv()

# Configure logging
def setup_logging():
    """Set up logging configuration"""
    log_dir = Path("logs")
    ensure_directory(log_dir)
    
    log_filename = f'logs/gpse_clean_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()


@CrewBase
class GPSECrewClean():
    """Clean GPSE Crew without custom ChromaDB configuration"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks_simplified.yaml'
    
    def __init__(self, inputs: Optional[Dict[str, Any]] = None):
        """Initialize the GPSE Crew"""
        self.inputs = inputs or {}
        self.project_root = Path(__file__).parent
        self.strategy_dir = self.project_root / "strategy_analyses"
        self.logs_dir = self.project_root / "logs"
        
        # Store analysis metadata
        self.analysis_metadata = {}
        
        ensure_directory(self.strategy_dir)
        ensure_directory(self.logs_dir)
        
        self._initialize_tools()
        self._initialize_llms()
        
        logger.info("Initialized GPSE Crew - CLEAN VERSION")
    
    def _initialize_tools(self):
        """Initialize all required tools"""
        self.db_query_tool = query_strategy_database
        self.enhanced_news_tool = enhanced_news_search
        self.url_fetch_tool = fetch_news_from_url
        self.news_aggregator_tool = aggregate_geopolitical_news
        self.file_writer_tool = FileWriterTool()
        self.communicator_db_tool = CommunicatorDBUpdateTool()
        
        logger.info("Tools initialized successfully")
    
    def _initialize_llms(self):
        """Initialize LLMs with better context window management"""
        self.llm_provider = os.getenv('LLM_PROVIDER', 'openai')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if self.llm_provider == 'anthropic' and self.anthropic_api_key:
            # Claude models have larger context windows
            self.powerful_llm = ChatAnthropic(
                model="claude-3-opus-20240229",
                api_key=self.anthropic_api_key,
                temperature=0.7,
                max_tokens=3000  # Reduced to leave room for context
            )
            self.efficient_llm = ChatAnthropic(
                model="claude-3-haiku-20240307",
                api_key=self.anthropic_api_key,
                temperature=0.7,
                max_tokens=1500
            )
            logger.info("Using Anthropic models with larger context windows")
        else:
            # Use GPT-4 Turbo with 128k context window
            self.powerful_llm = ChatOpenAI(
                model="gpt-4-0125-preview",  # Latest GPT-4 Turbo with 128k context
                api_key=self.openai_api_key,
                temperature=0.7,
                max_tokens=3000
            )
            # Use GPT-3.5 Turbo 16k for better context handling
            self.efficient_llm = ChatOpenAI(
                model="gpt-3.5-turbo-1106",  # 16k context version
                api_key=self.openai_api_key,
                temperature=0.7,
                max_tokens=1500
            )
            logger.info("Using OpenAI models with extended context windows")
    
    @before_kickoff
    def prepare_analysis(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare for analysis run"""
        logger.info("=" * 60)
        logger.info("GPSE - CLEAN VERSION")
        logger.info("=" * 60)
        logger.info(f"Starting at {get_timestamp()}")
        
        if not self._validate_environment():
            raise EnvironmentError("Environment validation failed")
        
        # Add all necessary metadata
        inputs['timestamp'] = datetime.now().isoformat()
        inputs['date_code'] = get_date_code()
        inputs['analysis_id'] = f"GGSM-{get_date_code()}-DailyAnalysis"
        
        # Store analysis metadata for post-processing
        self.analysis_metadata = {
            'analysis_id': inputs['analysis_id'],
            'timestamp': inputs['timestamp'],
            'date_code': inputs['date_code']
        }
        
        logger.info(f"Analysis ID: {inputs['analysis_id']}")
        return inputs
    
    @after_kickoff
    def post_process_results(self, result: Any) -> Any:
        """Post-process results"""
        logger.info("Post-processing results...")
        
        try:
            start_time = datetime.fromisoformat(self.analysis_metadata.get('timestamp', datetime.now().isoformat()))
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Execution time: {execution_time:.2f} seconds")
            
            # Use stored metadata instead of self.inputs
            expected_path = self.strategy_dir / f"{self.analysis_metadata['analysis_id']}.md"
            
            if expected_path.exists():
                logger.info(f"SUCCESS: Analysis saved to {expected_path}")
                logger.info(f"File size: {expected_path.stat().st_size} bytes")
            else:
                logger.error(f"FAILURE: Expected file not found: {expected_path}")
            
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Post-processing error: {e}")
            # Don't raise, just log the error
        
        return result
    
    @agent
    def news_scout(self) -> Agent:
        """News Scout with optimized output"""
        config = self.agents_config['news_scout'].copy()
        
        config['backstory'] = """Expert news researcher with access to multiple APIs.

CRITICAL INSTRUCTIONS:
1. Use 'Geopolitical News Aggregator' to gather news
2. Use 'Direct URL News Fetch' for key articles
3. LIMIT output to 5-7 most important articles
4. Keep summaries concise (2-3 sentences each)

OUTPUT FORMAT:
For each article provide:
- Title
- Source & Date
- 2-3 sentence summary
- Strategic relevance (1 sentence)

KEEP TOTAL OUTPUT UNDER 2000 WORDS to avoid context issues."""
        
        return Agent(
            config=config,
            tools=[self.news_aggregator_tool, self.enhanced_news_tool, self.url_fetch_tool],
            llm=self.efficient_llm,
            max_iter=5,
            memory=True,  # Let CrewAI handle memory configuration
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def geo_analyst(self) -> Agent:
        """Geopolitical Analyst with context management"""
        config = self.agents_config['geo_analyst'].copy()
        
        config['backstory'] = """Senior geopolitical strategist.

CRITICAL INSTRUCTIONS:
1. Query Strategy Database for historical context
2. Analyze news from scout's report
3. Create CONCISE strategic analysis

OUTPUT STRUCTURE (keep each section brief):
- Executive Summary (150 words max)
- 3-4 Primary Observations (200 words each max)
- Scenario Implications (200 words max)

TOTAL OUTPUT: 1500 words maximum"""
        
        return Agent(
            config=config,
            tools=[self.db_query_tool],
            llm=self.powerful_llm,
            max_iter=3,
            memory=True,  # Let CrewAI handle memory configuration
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def communicator(self) -> Agent:
        """Communicator with file saving focus"""
        base_agent = create_communicator_agent(self.powerful_llm)
        
        base_agent.backstory += """

EXECUTION REQUIREMENTS:
1. Format the analysis as GGSM document
2. SAVE using File Writer Tool with filename: GGSM-{date}-DailyAnalysis.md
   (DO NOT include 'strategy_analyses/' in the filename - the tool adds it automatically)
3. ADD to ChromaDB using Strategy Database Update Tool
4. Keep formatting clean and professional

MUST ACTUALLY EXECUTE - not describe!"""
        
        return base_agent
    
    @task
    def news_scout_task(self) -> Task:
        """Optimized news gathering task"""
        return Task(
            description="""Gather current geopolitical news:

1. Use 'Geopolitical News Aggregator' for:
   - Ukraine-Russia conflict
   - Middle East tensions
   - US-China relations
   - Major economic/cyber events

2. Select 5-7 MOST SIGNIFICANT articles
3. Use 'Direct URL News Fetch' for top 3-5 articles
4. Create CONCISE briefing (under 2000 words)

Focus on QUALITY over quantity.""",
            expected_output="Concise news briefing with 5-7 key articles, summaries, and strategic relevance",
            agent=self.news_scout()
        )
    
    @task
    def geo_analyst_task(self) -> Task:
        """Optimized analysis task"""
        return Task(
            description="""Create strategic analysis:

1. Query Strategy Database for context
2. Analyze news briefing
3. Produce GGSM-format analysis:
   - Executive Summary (150 words)
   - 3-4 Actor Observations (200 words each)
   - Scenario Implications (200 words)

Keep TOTAL under 1500 words.""",
            expected_output="Concise GGSM-format strategic analysis",
            agent=self.geo_analyst(),
            context=[self.news_scout_task()]
        )
    
    @task
    def communicator_task(self) -> Task:
        """File saving task - FIXED PATH ISSUE"""
        return Task(
            description=f"""SAVE the analysis:

1. Format as GGSM document
2. SAVE using File Writer Tool with filename: GGSM-{get_date_code()}-DailyAnalysis.md
   IMPORTANT: Do NOT include 'strategy_analyses/' in the filename!
3. ADD to ChromaDB using full path: strategy_analyses/GGSM-{get_date_code()}-DailyAnalysis.md
4. Report success

EXECUTE don't describe!""",
            expected_output="Confirmation of file saved and database updated",
            agent=self.communicator(),
            context=[self.geo_analyst_task()]
        )
    
    @crew
    def crew(self) -> Crew:
        """Clean crew configuration - let CrewAI handle ChromaDB"""
        memory_enabled = os.getenv('CREWAI_MEMORY_ENABLED', 'true').lower() == 'true'
        
        crew_config = {
            "agents": self.agents,
            "tasks": self.tasks,
            "process": Process.sequential,
            "memory": memory_enabled,
            "planning": False,  # Execution mode
            "verbose": True,
            "max_rpm": 10,
            "share_crew": False
        }
        
        # Only add embedder if memory is enabled
        if memory_enabled:
            crew_config["embedder"] = {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small"
                }
            }
        
        return Crew(**crew_config)
    
    def _validate_environment(self) -> bool:
        """Validate environment"""
        issues = []
        
        if not self.openai_api_key and not self.anthropic_api_key:
            issues.append("No LLM API key found")
        
        if not os.getenv('TAVILY_API_KEY'):
            issues.append("TAVILY_API_KEY not found")
        
        # Don't check ChromaDB here - let CrewAI handle it
        
        if issues:
            logger.error("Validation failed:")
            for issue in issues:
                logger.error(f"  - {issue}")
            return False
        
        logger.info("Environment validated")
        return True


def main():
    """Main execution"""
    try:
        logger.info("Starting GPSE Clean...")
        
        # Check if user wants to disable memory
        if len(sys.argv) > 1 and sys.argv[1] == '--no-memory':
            os.environ['CREWAI_MEMORY_ENABLED'] = 'false'
            logger.info("Memory disabled via command line")
        
        gpse_crew = GPSECrewClean()
        
        inputs = {
            "focus_areas": [
                "Ukraine-Russia conflict",
                "Middle East tensions",
                "US-China relations"
            ],
            "quality_threshold": 0.8,
            "time_window": "24 hours",
            "date": get_date_code()
        }
        
        crew_instance = gpse_crew.crew()
        
        logger.info("=" * 60)
        logger.info("EXECUTING CLEAN CREW...")
        logger.info("Using CrewAI's default memory configuration")
        logger.info("=" * 60)
        
        result = crew_instance.kickoff(inputs=inputs)
        
        # Safe result logging
        try:
            if hasattr(result, 'raw'):
                logger.info(f"Result preview: {str(result.raw)[:300]}...")
            else:
                logger.info("Result received (details not stringifiable)")
        except:
            logger.info("Result received")
        
        # Verify file creation
        expected_file = Path(f"strategy_analyses/GGSM-{get_date_code()}-DailyAnalysis.md")
        if expected_file.exists():
            logger.info(f"SUCCESS: {expected_file}")
            with open(expected_file, 'r', encoding='utf-8') as f:
                preview = f.read()[:500]
                logger.info(f"File preview:\n{preview}...")
        else:
            logger.error("FAILURE: No file created")
        
        return result
        
    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
        
        # If it's a ChromaDB error, suggest running without memory
        if "chromadb" in str(e).lower() or "database" in str(e).lower():
            logger.info("\n" + "="*60)
            logger.info("TIP: If you're getting ChromaDB errors, try running without memory:")
            logger.info("     python main_crew_clean.py --no-memory")
            logger.info("="*60 + "\n")
        
        raise


if __name__ == "__main__":
    main()
