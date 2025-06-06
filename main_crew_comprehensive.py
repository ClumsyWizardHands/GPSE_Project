"""
GPSE Main Crew - Comprehensive Version
Enhanced version that creates comprehensive reports combining outputs from both agents
"""

import os
import sys
import logging
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv

# Import CrewAI
from crewai import Agent, Task, Crew, Process

# Import LangChain LLM modules
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

# Import tools
from gpse_tools_comprehensive import (
    enhanced_news_search,
    fetch_news_from_url,
    aggregate_geopolitical_news,
    query_strategy_database
)

# Import comprehensive save tools for Communicator
from gpse_tools_comprehensive_save import (
    save_comprehensive_analysis,
    extract_comprehensive_analysis
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/gpse_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create required directories
os.makedirs('logs', exist_ok=True)
os.makedirs('strategy_analyses', exist_ok=True)

class GPSECrew:
    """Production GPSE Crew with comprehensive reporting"""
    
    def __init__(self):
        """Initialize the GPSE Crew"""
        try:
            logger.info("=== INITIALIZING GPSE CREW (COMPREHENSIVE VERSION) ===")
            
            # Load configurations
            self.agents_config = self._load_config('config/agents.yaml')
            self.tasks_config = self._load_config('config/tasks_fixed.yaml')
            
            # Initialize shared tools
            self.news_tool = enhanced_news_search
            self.url_fetch_tool = fetch_news_from_url
            self.aggregator_tool = aggregate_geopolitical_news
            self.database_tool = query_strategy_database
            
            # Initialize Communicator tools
            self.save_analysis_tool = save_comprehensive_analysis
            self.extract_content_tool = extract_comprehensive_analysis
            
            logger.info("All tools initialized successfully")
            
            # Get current date for context
            self.current_date = datetime.now().strftime("%B %d, %Y")
            
            # Initialize output filepath
            output_filename = f'strategy_analyses/GGSM-{self.current_date}-DailyAnalysis.md'
            self.output_filepath = os.path.abspath(output_filename)
            
            # Initialize LLM instances for each agent
            self._initialize_llms()
            
            # Set up enhanced news search parameters
            self.news_search_config = {
                'max_results_per_query': 10,
                'search_queries': [
                    f"geopolitical news {self.current_date}",
                    "China US Russia tensions today",
                    "military developments global",
                    "diplomatic summit meeting today",
                    "economic sanctions trade war",
                    "NATO alliance news",
                    "Middle East conflict update",
                    "technology export controls"
                ]
            }
            
            logger.info("GPSE Crew initialized successfully with comprehensive reporting")
            
        except Exception as e:
            logger.error(f"Failed to initialize GPSE Crew: {str(e)}")
            raise
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            logger.info(f"Successfully loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {str(e)}")
            raise
    
    def _initialize_llms(self):
        """Initialize different LLM configurations for each agent"""
        # News Scout: Claude 3.5 Haiku for fast, efficient news processing
        self.news_scout_llm = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            temperature=0.7,
            max_tokens=4000,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        logger.info("News Scout LLM: Claude 3.5 Haiku")
        
        # Geopolitical Analyst: GPT-4o for deep reasoning
        self.geo_analyst_llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.5,
            max_tokens=8000,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        logger.info("Geopolitical Analyst LLM: GPT-4o")
        
        # Communicator: GPT-4o Mini for efficient output
        self.communicator_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=4000,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        logger.info("Communicator LLM: GPT-4o Mini")
    
    def news_scout(self) -> Agent:
        """Create News Scout Agent"""
        config = self.agents_config['news_scout']
        
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[self.news_tool, self.aggregator_tool, self.url_fetch_tool],
            llm=self.news_scout_llm,
            max_iter=5,
            verbose=True,
            memory=False
        )
    
    def geo_analyst(self) -> Agent:
        """Create Geopolitical Analyst Agent"""
        config = self.agents_config['geo_analyst']
        
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[self.database_tool, self.news_tool],
            llm=self.geo_analyst_llm,
            max_iter=5,
            verbose=True,
            memory=False
        )
    
    def communicator(self) -> Agent:
        """Create Strategic Communicator Agent with comprehensive save tools"""
        config = self.agents_config['communicator']
        
        # Enhanced goal and backstory for comprehensive reporting
        enhanced_goal = """Extract and combine outputs from BOTH the News Scout and Geo Analyst to create 
        a comprehensive strategic analysis document. The document should include the main strategic analysis 
        AND a news intelligence appendix."""
        
        enhanced_backstory = config['backstory'] + """
        
        CRITICAL MISSION: You must create COMPREHENSIVE reports that include:
        1. The main strategic analysis from the Geo Analyst
        2. A news intelligence appendix from the News Scout
        
        This creates a complete intelligence product with both analysis and source data.
        Use the Extract Comprehensive Analysis tool first to separate the outputs,
        then use Save Comprehensive Analysis to create the final document."""
        
        return Agent(
            role=config['role'],
            goal=enhanced_goal,
            backstory=enhanced_backstory,
            tools=[self.extract_content_tool, self.save_analysis_tool],
            llm=self.communicator_llm,
            max_iter=3,
            verbose=True,
            memory=False
        )
    
    def scout_task(self) -> Task:
        """Create news scouting task"""
        config = self.tasks_config['news_scout_task']
        
        # Replace date placeholder
        description = config['description'].replace('{current_date}', self.current_date)
        
        # Add enhanced search parameters
        enhanced_description = f"""{description}
        
        ENHANCED SEARCH PARAMETERS:
        - Search multiple queries: {', '.join(self.news_search_config['search_queries'])}
        - Collect at least {self.news_search_config['max_results_per_query']} articles per query
        - Total target: 50+ unique articles from diverse sources
        - Focus on recent 24-48 hours
        
        CRITICAL: Use ALL available tools multiple times to gather comprehensive data.
        Format your output with clear structure including titles, URLs, dates, and sources."""
        
        task = Task(
            description=enhanced_description,
            expected_output=config['expected_output'],
            agent=self.news_scout()
        )
        
        # Store reference for context passing
        self.news_scout_task_ref = task
        return task
    
    def analysis_task(self) -> Task:
        """Create strategic analysis task"""
        config = self.tasks_config['geo_analyst_task']
        
        # Replace date placeholder
        description = config['description'].replace('{current_date}', self.current_date)
        
        task = Task(
            description=description,
            expected_output=config['expected_output'],
            agent=self.geo_analyst(),
            context=[self.news_scout_task_ref]
        )
        
        # Store reference for context passing
        self.geo_analyst_task_ref = task
        return task
    
    def communication_task(self) -> Task:
        """Create comprehensive communication task"""
        
        # Enhanced description for comprehensive reporting
        description = f"""Your mission is to create a COMPREHENSIVE strategic analysis document that combines:

1. Extract outputs from BOTH agents using the Extract Comprehensive Analysis tool
2. Combine them into a single comprehensive document that includes:
   - The full strategic analysis from the Geo Analyst (main content)
   - A news intelligence appendix from the News Scout (appendix)
3. Save the comprehensive document using the Save Comprehensive Analysis tool

Current date: {self.current_date}

CRITICAL INSTRUCTIONS:
- First, use Extract Comprehensive Analysis to separate the News Scout and Geo Analyst outputs
- Then, use Save Comprehensive Analysis with the extracted content to create the final document
- The document should provide both strategic insights AND source transparency
- DO NOT create a quality assessment report - create the actual comprehensive analysis

The absolute file path for saving is: {self.output_filepath}"""
        
        task = Task(
            description=description,
            expected_output="Confirmation that the comprehensive strategic analysis document has been saved, including both main analysis and news appendix",
            agent=self.communicator(),
            context=[self.news_scout_task_ref, self.geo_analyst_task_ref],
            output_file=f'strategy_analyses/GGSM-{self.current_date}-DailyAnalysis.md'
        )
        
        return task
    
    def crew(self) -> Crew:
        """Create and configure the crew"""
        logger.info("Creating crew with comprehensive reporting capability")
        
        # Create tasks in order (important for context references)
        scout_task = self.scout_task()
        analysis_task = self.analysis_task()
        comm_task = self.communication_task()
        
        agents = [
            self.news_scout(),
            self.geo_analyst(),
            self.communicator()
        ]
        
        tasks = [scout_task, analysis_task, comm_task]
        
        logger.info(f"Created {len(agents)} agents and {len(tasks)} tasks")
        
        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            memory=False
        )

def main():
    """Main execution function"""
    output_filepath = None
    
    try:
        print("\n" + "="*60)
        print("GEOPOLITICAL GRAND STRATEGY ENGINE (GPSE)")
        print("COMPREHENSIVE REPORTING VERSION")
        print("="*60 + "\n")
        
        print(f"Execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Logs will be saved to: logs/")
        print(f"Analysis will be saved to: strategy_analyses/")
        print("\nThis version creates comprehensive reports with:")
        print("- Main strategic analysis")
        print("- News intelligence appendix")
        
        logger.info("Starting GPSE with comprehensive reporting...")
        
        # Initialize crew
        gpse_crew = GPSECrew()
        
        # Store the output filepath
        output_filepath = gpse_crew.output_filepath
        
        # Create crew instance
        crew_instance = gpse_crew.crew()
        
        # Execute crew
        logger.info("Executing GPSE crew...")
        result = crew_instance.kickoff()
        
        logger.info("GPSE execution completed!")
        
        # Display results
        print("\n" + "="*50)
        print("GPSE ANALYSIS COMPLETE")
        print("="*50)
        print(f"\nAnalysis saved to: {output_filepath}")
        print(f"Logs saved to: logs/")
        
        # Verify the output file
        if os.path.exists(output_filepath):
            print(f"\n✓ SUCCESS: Comprehensive analysis file created")
            with open(output_filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check for both analysis and appendix
                has_analysis = "Executive Summary" in content or "Primary Observations" in content
                has_appendix = "Appendix" in content or "News Intelligence" in content
                
                if has_analysis and has_appendix:
                    print("✓ VERIFIED: File contains both strategic analysis and news appendix")
                elif has_analysis:
                    print("✓ PARTIAL: File contains strategic analysis (appendix may be missing)")
                else:
                    print("⚠ WARNING: File may not contain expected sections")
        else:
            print(f"\n✗ ERROR: Expected file not found")
        
        print("\nAnalysis Summary:")
        print("-" * 50)
        if result:
            # Print first 1000 characters of result
            result_str = str(result)
            if len(result_str) > 1000:
                print(result_str[:1000] + "...")
            else:
                print(result_str)
        
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        print("\n" + "="*60)
        print("ERROR DURING EXECUTION")
        print("="*60)
        print(f"Error: {str(e)}")
        
        logger.exception("Full traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()
