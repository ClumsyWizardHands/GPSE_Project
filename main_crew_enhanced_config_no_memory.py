"""
GPSE Main Crew - Enhanced with Config Loading and Debug (No Memory Version)
Uses configuration files and adds extensive debugging
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

# Now import CrewAI
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

# Configure enhanced logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for maximum verbosity
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/gpse_debug_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create logs directory
os.makedirs('logs', exist_ok=True)
os.makedirs('debug_outputs', exist_ok=True)

class GPSECrewEnhanced:
    """Enhanced GPSE Crew with Config Loading and Debug"""
    
    def __init__(self):
        """Initialize the Enhanced GPSE Crew"""
        try:
            logger.info("=== INITIALIZING ENHANCED GPSE CREW ===")
            
            # Load configurations
            self.agents_config = self._load_config('config/agents.yaml')
            self.tasks_config = self._load_config('config/tasks_simplified.yaml')
            
            # Initialize shared tools
            self.news_tool = enhanced_news_search
            self.url_fetch_tool = fetch_news_from_url
            self.aggregator_tool = aggregate_geopolitical_news
            self.database_tool = query_strategy_database
            
            logger.info("Tools initialized successfully")
            
            # Get current date for context
            self.current_date = datetime.now().strftime("%B %d, %Y")
            
            # Initialize output filepath
            output_filename = f'strategy_analyses/GGSM-{self.current_date}-DailyAnalysis.md'
            self.output_filepath = os.path.abspath(output_filename)
            
            # Initialize LLM instances for each agent
            self._initialize_llms()
            
            # Set up enhanced news search parameters
            self.news_search_config = {
                'max_results_per_query': 10,  # Increased from default
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
            
            logger.info("Enhanced GPSE Crew initialized with config loading")
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced GPSE Crew: {str(e)}")
            raise
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            logger.info(f"Loading configuration from: {config_path}")
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            logger.info(f"Successfully loaded {len(config)} items from {config_path}")
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
        logger.info("News Scout LLM: Claude 3.5 Haiku (fast processing)")
        
        # Geopolitical Analyst: GPT-4o (OpenAI's reasoning model)
        self.geo_analyst_llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.5,
            max_tokens=8000,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        logger.info("Geopolitical Analyst LLM: GPT-4o (deep reasoning)")
        
        # Communicator: GPT-4o Mini
        self.communicator_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=4000,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        logger.info("Communicator LLM: GPT-4o Mini (efficient output)")
    
    def news_scout(self) -> Agent:
        """Create News Scout Agent from config"""
        config = self.agents_config['news_scout']
        logger.debug(f"Creating News Scout with config: {json.dumps(config, indent=2)}")
        
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[self.news_tool, self.aggregator_tool, self.url_fetch_tool],
            llm=self.news_scout_llm,
            max_iter=5,  # Increased iterations
            verbose=True,
            memory=False,  # DISABLED
            callbacks=[self._agent_callback]
        )
    
    def geo_analyst(self) -> Agent:
        """Create Geopolitical Analyst Agent from config"""
        config = self.agents_config['geo_analyst']
        logger.debug(f"Creating Geo Analyst with config: {json.dumps(config, indent=2)}")
        
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[self.database_tool, self.news_tool],
            llm=self.geo_analyst_llm,
            max_iter=5,  # Increased iterations
            verbose=True,
            memory=False,  # DISABLED
            callbacks=[self._agent_callback]
        )
    
    def communicator(self) -> Agent:
        """Create Strategic Communicator Agent from config"""
        config = self.agents_config['communicator']
        logger.debug(f"Creating Communicator with config: {json.dumps(config, indent=2)}")
        
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[],
            llm=self.communicator_llm,
            max_iter=3,
            verbose=True,
            memory=False,  # DISABLED
            callbacks=[self._agent_callback]
        )
    
    def scout_task(self) -> Task:
        """Create news scouting task from config"""
        config = self.tasks_config['news_scout_task']
        
        # Replace date placeholder
        description = config['description'].replace('{current_date}', self.current_date)
        
        # Add enhanced search parameters to the description
        enhanced_description = f"""{description}
        
        ENHANCED SEARCH PARAMETERS:
        - Search multiple queries: {', '.join(self.news_search_config['search_queries'])}
        - Collect at least {self.news_search_config['max_results_per_query']} articles per query
        - Total target: 50+ unique articles from diverse sources
        - Focus on recent 24-48 hours
        
        CRITICAL: Use ALL available tools multiple times to gather comprehensive data."""
        
        logger.debug(f"Creating Scout Task with enhanced description: {enhanced_description[:500]}...")
        
        return Task(
            description=enhanced_description,
            expected_output=config['expected_output'],
            agent=self.news_scout(),
            callbacks=[self._task_callback]
        )
    
    def analysis_task(self) -> Task:
        """Create strategic analysis task from config"""
        config = self.tasks_config['geo_analyst_task']
        
        # Replace date placeholder
        description = config['description'].replace('{current_date}', self.current_date)
        
        logger.debug(f"Creating Analysis Task with description: {description[:500]}...")
        
        return Task(
            description=description,
            expected_output=config['expected_output'],
            agent=self.geo_analyst(),
            callbacks=[self._task_callback]
        )
    
    def communication_task(self) -> Task:
        """Create strategic communication task from config"""
        config = self.tasks_config['communicator_task']
        
        # Replace placeholders
        description = config['description'].replace('{current_date}', self.current_date)
        output_filename = f'strategy_analyses/GGSM-{self.current_date}-DailyAnalysis.md'
        
        # Add explicit save instruction
        enhanced_description = f"""{description}
        
        CRITICAL: After saving the document to {output_filename}, 
        you MUST include the absolute file path in your response: {self.output_filepath}"""
        
        logger.debug(f"Creating Communication Task with enhanced description: {enhanced_description[:500]}...")
        
        return Task(
            description=enhanced_description,
            expected_output=config['expected_output'],
            agent=self.communicator(),
            output_file=output_filename,
            callbacks=[self._task_callback]
        )
    
    def _agent_callback(self, agent_output):
        """Callback to log and save agent outputs"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            agent_name = getattr(agent_output, 'agent_name', 'unknown')
            
            logger.info(f"=== AGENT OUTPUT: {agent_name} ===")
            logger.info(f"Output: {str(agent_output)[:1000]}...")
            
            # Save to debug file
            debug_file = f"debug_outputs/{agent_name}_{timestamp}.txt"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"Agent: {agent_name}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Output:\n{str(agent_output)}\n")
            
            logger.info(f"Agent output saved to: {debug_file}")
        except Exception as e:
            logger.error(f"Error in agent callback: {str(e)}")
    
    def _task_callback(self, task_output):
        """Callback to log and save task outputs"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            task_name = getattr(task_output, 'description', 'unknown')[:50]
            
            logger.info(f"=== TASK OUTPUT ===")
            logger.info(f"Task: {task_name}")
            logger.info(f"Output: {str(task_output)[:1000]}...")
            
            # Save to debug file
            debug_file = f"debug_outputs/task_{timestamp}.txt"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"Task: {task_name}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Output:\n{str(task_output)}\n")
            
            logger.info(f"Task output saved to: {debug_file}")
        except Exception as e:
            logger.error(f"Error in task callback: {str(e)}")
    
    def crew(self) -> Crew:
        """Create and configure the crew"""
        logger.info("Creating enhanced crew with config-loaded agents and tasks")
        
        agents = [
            self.news_scout(),
            self.geo_analyst(),
            self.communicator()
        ]
        
        tasks = [
            self.scout_task(),
            self.analysis_task(),
            self.communication_task()
        ]
        
        logger.info(f"Created {len(agents)} agents and {len(tasks)} tasks")
        
        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,  # DISABLED
            callbacks=[self._crew_callback]
        )
    
    def _crew_callback(self, crew_output):
        """Callback to log crew execution"""
        try:
            logger.info("=== CREW EXECUTION COMPLETE ===")
            logger.info(f"Final output: {str(crew_output)[:2000]}...")
            
            # Save final output
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_file = f"debug_outputs/crew_final_{timestamp}.txt"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"Crew Final Output\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Output:\n{str(crew_output)}\n")
            
            logger.info(f"Crew output saved to: {debug_file}")
        except Exception as e:
            logger.error(f"Error in crew callback: {str(e)}")

def main():
    """Main execution function"""
    output_filepath = None
    
    try:
        print("\n" + "="*60)
        print("GEOPOLITICAL GRAND STRATEGY ENGINE (GPSE)")
        print("Enhanced Version with Config Loading and Debug (NO MEMORY)")
        print("="*60 + "\n")
        
        print(f"Execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Debug outputs will be saved to: debug_outputs/")
        print(f"Logs will be saved to: logs/")
        print("Memory: DISABLED (to bypass ChromaDB issues)")
        
        logger.info("Starting Enhanced GPSE (No Memory)...")
        
        # Create output directories
        os.makedirs('strategy_analyses', exist_ok=True)
        os.makedirs('debug_outputs', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Initialize enhanced crew
        gpse_crew = GPSECrewEnhanced()
        
        # Store the output filepath
        output_filepath = gpse_crew.output_filepath
        
        # Log configuration status
        logger.info(f"Loaded {len(gpse_crew.agents_config)} agent configs")
        logger.info(f"Loaded {len(gpse_crew.tasks_config)} task configs")
        logger.info(f"Using {len(gpse_crew.news_search_config['search_queries'])} search queries")
        
        # Create crew instance
        crew_instance = gpse_crew.crew()
        
        # Execute crew
        logger.info("Executing Enhanced GPSE crew...")
        result = crew_instance.kickoff()
        
        logger.info("Enhanced GPSE execution completed successfully!")
        logger.info(f"Results: {result}")
        
        # Display results
        print("\n" + "="*50)
        print("ENHANCED GPSE ANALYSIS COMPLETE")
        print("="*50)
        print(f"\nAnalysis saved to: {output_filepath}")
        print(f"\nDebug outputs saved to: debug_outputs/")
        print(f"Logs saved to: logs/")
        print("\nKey Findings:")
        print("-" * 50)
        if result:
            print(result)
        
        # Print the absolute file path as the very last line
        print(output_filepath)
        
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
