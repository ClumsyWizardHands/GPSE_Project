"""
GPSE Main Crew Orchestration Script
Coordinates the multi-agent system for daily geopolitical analysis
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# CrewAI imports
from crewai import Agent, Crew, Task, Process
from crewai.agent import Agent
from crewai.task import Task

# LangChain imports for LLM initialization
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Import custom tools
from gpse_tools import (
    StrategyDBQueryTool,
    StrategyDBUpdateTool,
    TavilyNewsSearchTool,
    SimpleWebScraperTool,
    get_date_code,
    get_timestamp,
    ensure_directory
)

# Import database manager functions
from db_manager import process_strategy_document

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/gpse_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class GPSECrew:
    """Main orchestration class for the GPSE multi-agent system."""
    
    def __init__(self):
        """Initialize the GPSE Crew with configuration and tools."""
        self.project_root = Path(__file__).parent
        self.strategy_dir = self.project_root / "strategy_analyses"
        self.logs_dir = self.project_root / "logs"
        
        # Ensure required directories exist
        ensure_directory(self.strategy_dir)
        ensure_directory(self.logs_dir)
        
        # Initialize tools
        self.db_query_tool = StrategyDBQueryTool().tool
        self.db_update_tool = StrategyDBUpdateTool().tool
        self.news_search_tool = TavilyNewsSearchTool().tool
        self.web_scraper_tool = SimpleWebScraperTool().tool
        
        # Get LLM configuration from environment
        self.llm_provider = os.getenv('LLM_PROVIDER', 'openai')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Initialize LLM instances based on provider
        if self.llm_provider == 'anthropic' and self.anthropic_api_key:
            # Use Anthropic models
            self.analyst_llm = ChatAnthropic(
                model="claude-3-opus-20240229",
                api_key=self.anthropic_api_key,
                temperature=0.7,
                max_tokens=4000
            )
            self.support_llm = ChatAnthropic(
                model="claude-3-haiku-20240307",
                api_key=self.anthropic_api_key,
                temperature=0.7,
                max_tokens=2000
            )
            logger.info("Initialized Anthropic LLMs: Claude 3 Opus for analyst, Claude 3 Haiku for support")
        else:
            # Use OpenAI models (default)
            self.analyst_llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                api_key=self.openai_api_key,
                temperature=0.7,
                max_tokens=4000
            )
            self.support_llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                api_key=self.openai_api_key,
                temperature=0.7,
                max_tokens=2000
            )
            logger.info("Initialized OpenAI LLMs: GPT-4 Turbo for analyst, GPT-3.5 Turbo for support")
        
        logger.info(f"Initialized GPSE Crew with LLM provider: {self.llm_provider}")
        
    def create_agents(self) -> Dict[str, Agent]:
        """Create and configure the specialized agents."""
        
        # News Scout Agent
        news_scout = Agent(
            role='Expert Global News Researcher',
            goal='Discover and compile the most recent and significant news articles regarding specified global political topics from the last 24-48 hours.',
            backstory='A diligent news analyst specializing in identifying pivotal geopolitical events.',
            verbose=True,
            allow_delegation=False,
            tools=[self.news_search_tool, self.web_scraper_tool],
            llm=self.support_llm
        )
        
        # Information Curation Specialist
        info_curator = Agent(
            role='Information Curation Specialist',
            goal='Gather and synthesize recent global political news and events from multiple sources',
            backstory="""You are an expert information analyst specializing in global political affairs. 
            Your role is to efficiently gather, filter, and pre-process news from various sources to 
            identify the most significant geopolitical developments. You excel at distinguishing signal 
            from noise and preparing structured briefings for strategic analysis.""",
            verbose=True,
            allow_delegation=False,
            tools=[self.news_search_tool, self.web_scraper_tool],
            llm=self.support_llm
        )
        
        # Lead Strategy Analyst
        strategy_analyst = Agent(
            role='Lead Strategy Analyst',
            goal='Produce comprehensive strategic analyses by synthesizing current events with historical context',
            backstory="""You are a senior geopolitical strategist with decades of experience analyzing 
            international relations, state behavior, and strategic trends. You specialize in identifying 
            patterns, understanding multi-actor dynamics, and inferring various perspectives on future 
            developments. You draw upon extensive historical knowledge to contextualize current events 
            and provide nuanced, multi-perspective strategic assessments.""",
            verbose=True,
            allow_delegation=False,
            tools=[self.db_query_tool],
            llm=self.analyst_llm
        )
        
        # Communications & Archival Lead
        comms_archival = Agent(
            role='Communications & Archival Lead',
            goal='Format analyses into standardized documents and maintain the knowledge base',
            backstory="""You are responsible for transforming strategic analyses into clear, actionable 
            documents following established formats. You ensure consistency in documentation, maintain 
            the integrity of the knowledge base, and prepare materials for distribution. Your work 
            enables the accumulation of institutional knowledge over time.""",
            verbose=True,
            allow_delegation=False,
            tools=[self.db_update_tool],
            llm=self.support_llm
        )
        
        return {
            'news_scout': news_scout,
            'info_curator': info_curator,
            'strategy_analyst': strategy_analyst,
            'comms_archival': comms_archival
        }
    
    def create_tasks(self, agents: Dict[str, Agent]) -> List[Task]:
        """Create the sequence of tasks for the analysis pipeline."""
        
        # Task 1: News Scouting - Deep search for strategic intelligence
        news_scout_task = Task(
            description="""Search for top news articles from the last 24-48 hours focusing on:
            
            1. Active or escalating warzones and battlefronts (e.g., Ukraine-Russia, Israel-Gaza, Red Sea, South China Sea).
            
            2. Strategic atrocities or human rights violations with potential geopolitical fallout (e.g., ethnic cleansing, forced displacement, infrastructure targeting).
            
            3. Emerging alignments or support behaviors among major powers (U.S., China, Russia, India, EU, Iran, etc.)—including arms deals, diplomatic cover, vetoes, and intelligence sharing.
            
            4. Signs of proxy conflict, covert escalation, or supply chain manipulation (e.g., satellite imagery leaks, unusual troop movements, naval surveillance incidents).
            
            5. State-enabled cyber warfare, disinformation campaigns, or financial coercion tactics.
            
            For each relevant article, extract its main content. Compile a structured output with URLs and their extracted content.""",
            expected_output="""A list/report of relevant news articles with their URLs and key text content.
            
            Format each entry as:
            - **URL**: [Full URL]
            - **Source**: [News outlet name]
            - **Date**: [Publication date]
            - **Title**: [Article title]
            - **Strategic Category**: [Which of the 5 focus areas it relates to]
            - **Key Content**: [Extracted main points, quotes, and strategic relevance]
            - **Entities Mentioned**: [Countries, leaders, organizations involved]
            
            Organize by strategic category and prioritize by geopolitical significance.""",
            agent=agents['news_scout']
        )
        
        # Task 2: Information Gathering and Synthesis
        gather_news_task = Task(
            description="""Gather recent global political news and events from the past 24-48 hours.
            Focus on:
            1. Major geopolitical developments and state actions
            2. International relations shifts and diplomatic events
            3. Military movements and security developments
            4. Political leadership changes and policy announcements
            5. Regional conflicts and tensions
            
            Use the news search tool to find relevant articles, then use the web scraper for 
            important stories needing more detail. Organize findings by region/country and 
            prioritize by strategic significance.""",
            expected_output="""A structured briefing containing:
            - Executive overview of key developments (3-5 bullet points)
            - Detailed findings organized by country/region
            - For each item: summary, source, date, and strategic relevance
            - Identification of emerging patterns or connected events""",
            agent=agents['info_curator'],
            context=[news_scout_task]
        )
        
        # Task 3: Strategic Analysis
        analyze_strategy_task = Task(
            description="""Conduct deep strategic analysis of the gathered information.
            
            Process:
            1. Query the strategy database for relevant historical context on key actors/regions
            2. Analyze new developments against historical patterns
            3. Identify strategic shifts, emerging trends, and potential risks
            4. Consider multiple perspectives (US, China, Russia, EU, regional powers)
            5. Assess emotion signals, identity factors, and historical resentments
            6. Project potential scenarios and implications
            
            Your analysis should be nuanced, acknowledging uncertainty while providing 
            actionable insights. Focus on inference over prediction.""",
            expected_output="""A comprehensive strategic analysis following this structure:
            
            ### Executive Summary
            - High-level synthesis of global strategic environment
            - Key developments and their implications
            - Major risks and opportunities identified
            
            ### Primary Observations
            For each significant country/actor:
            - Observable Behavior: What actions have they taken?
            - Inferred Strategic Shift: What might this indicate about their strategy?
            - Emotion Signals/Identity/Resentments: Deeper motivational factors
            - Historical Context: How does this compare to past behavior?
            
            ### Trend Analysis
            - Emerging patterns across multiple actors
            - Shifts in global/regional power dynamics
            - Technology, economic, or social factors affecting geopolitics
            
            ### Scenario Implications
            - 2-3 potential future scenarios based on current trends
            - Key indicators to watch
            - Recommended areas for continued monitoring""",
            agent=agents['strategy_analyst'],
            context=[gather_news_task]
        )
        
        # Task 4: Documentation and Archival
        document_archive_task = Task(
            description="""Format the strategic analysis into a standardized document and update 
            the knowledge base.
            
            Steps:
            1. Create a properly formatted markdown document following the STRATEGY-MMDDYY-Description.md 
               naming convention
            2. Ensure the document includes all required sections with proper headers
            3. Generate a unique entry ID for the analysis
            4. Add metadata block with date, ID, and key topics
            5. Save the document to the strategy_analyses directory
            6. Process the document to add it to ChromaDB with appropriate chunking
            
            Use the established document template and maintain consistency with previous analyses.""",
            expected_output="""Confirmation of successful completion including:
            - Filename of saved analysis document
            - Entry ID assigned
            - Number of chunks added to database
            - Brief summary of key topics covered""",
            agent=agents['comms_archival'],
            context=[analyze_strategy_task]
        )
        
        return [news_scout_task, gather_news_task, analyze_strategy_task, document_archive_task]
    
    def generate_analysis_filename(self) -> str:
        """Generate a standardized filename for the analysis document."""
        date_code = get_date_code()
        return f"GGSM-{date_code}-DailyAnalysis.md"
    
    def format_analysis_document(self, analysis_content: str) -> str:
        """Format the analysis content into the standardized document structure."""
        timestamp = get_timestamp("%B %d, %Y")
        entry_id = f"GGSM-{get_date_code()}-DA"
        
        document = f"""---
## Geopolitical Grand Strategy Monitor
**Strategic Synthesis Entry**
**Date:** {timestamp}
**Entry ID:** {entry_id}

{analysis_content}

---

*This analysis was generated by the GPSE automated system. It represents an AI-driven synthesis 
of current events and historical patterns, intended to support strategic awareness and decision-making.*
"""
        return document
    
    def run_analysis(self) -> Dict[str, Any]:
        """Execute the full analysis pipeline."""
        try:
            logger.info("Starting GPSE analysis run...")
            start_time = datetime.now()
            
            # Create agents
            agents = self.create_agents()
            logger.info("Created all agents successfully")
            
            # Create tasks
            tasks = self.create_tasks(agents)
            logger.info(f"Created {len(tasks)} tasks for execution")
            
            # Create and configure the crew
            crew = Crew(
                agents=list(agents.values()),
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            
            # Execute the crew's tasks
            logger.info("Beginning crew execution...")
            result = crew.kickoff()
            
            # Process results
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Analysis completed in {execution_time:.2f} seconds")
            
            # Save the final analysis
            if result:
                filename = self.generate_analysis_filename()
                filepath = self.strategy_dir / filename
                
                # Extract the analysis content from the result
                # The last task's output contains the formatted analysis
                analysis_content = str(result)
                formatted_doc = self.format_analysis_document(analysis_content)
                
                # Write to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(formatted_doc)
                
                logger.info(f"Saved analysis to: {filepath}")
                
                # Process the document for ChromaDB
                try:
                    process_strategy_document(str(filepath))
                    logger.info("Successfully added analysis to ChromaDB")
                except Exception as e:
                    logger.error(f"Error adding to ChromaDB: {e}")
                
                return {
                    'success': True,
                    'filename': filename,
                    'execution_time': execution_time,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error("No result returned from crew execution")
                return {
                    'success': False,
                    'error': 'No result from crew execution',
                    'execution_time': execution_time
                }
                
        except Exception as e:
            logger.error(f"Error during analysis run: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def validate_environment(self) -> bool:
        """Validate that all required environment variables and APIs are configured."""
        issues = []
        
        # Check LLM API keys
        if not self.openai_api_key and not self.anthropic_api_key:
            issues.append("No LLM API key found (need OPENAI_API_KEY or ANTHROPIC_API_KEY)")
        
        # Check Tavily API key
        if not os.getenv('TAVILY_API_KEY'):
            issues.append("TAVILY_API_KEY not found in environment")
        
        # Check directories
        if not self.strategy_dir.exists():
            try:
                self.strategy_dir.mkdir(parents=True)
            except Exception as e:
                issues.append(f"Cannot create strategy directory: {e}")
        
        if issues:
            logger.error("Environment validation failed:")
            for issue in issues:
                logger.error(f"  - {issue}")
            return False
        
        logger.info("Environment validation passed")
        return True


def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("GPSE - Geopolitical Grand Strategy Engine")
    logger.info("=" * 60)
    
    # Create crew instance
    crew = GPSECrew()
    
    # Validate environment
    if not crew.validate_environment():
        logger.error("Please fix environment issues before running")
        sys.exit(1)
    
    # Run analysis
    logger.info(f"Starting analysis at {get_timestamp()}")
    result = crew.run_analysis()
    
    # Report results
    if result['success']:
        logger.info("=" * 60)
        logger.info("Analysis completed successfully!")
        logger.info(f"Output file: {result.get('filename')}")
        logger.info(f"Execution time: {result.get('execution_time', 0):.2f} seconds")
        logger.info("=" * 60)
    else:
        logger.error("=" * 60)
        logger.error("Analysis failed!")
        logger.error(f"Error: {result.get('error')}")
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    # Run the main function
    main()
