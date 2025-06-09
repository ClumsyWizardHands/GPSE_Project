"""
GPSE Main Crew - Fixed Communicator Version
Ensures the Communicator saves the actual strategic analysis, not a QA report
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

# Import custom save tools for Communicator
from gpse_tools_save_analysis import (
    save_strategic_analysis,
    extract_analysis_content
)

# Configure enhanced logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/gpse_fixed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create required directories
os.makedirs('logs', exist_ok=True)
os.makedirs('debug_outputs', exist_ok=True)
os.makedirs('strategy_analyses', exist_ok=True)

class GPSECrewFixed:
    """Fixed GPSE Crew with proper Communicator implementation"""
    
    def __init__(self):
        """Initialize the Fixed GPSE Crew"""
        try:
            logger.info("=== INITIALIZING FIXED GPSE CREW ===")
            
            # Load configurations
            self.agents_config = self._load_config('config/agents.yaml')
            # Use the fixed tasks configuration
            self.tasks_config = self._load_config('config/tasks_fixed.yaml')
            
            # Initialize shared tools
            self.news_tool = enhanced_news_search
            self.url_fetch_tool = fetch_news_from_url
            self.aggregator_tool = aggregate_geopolitical_news
            self.database_tool = query_strategy_database
            
            # Initialize Communicator tools
            self.save_analysis_tool = save_strategic_analysis
            self.extract_content_tool = extract_analysis_content
            
            logger.info("All tools initialized successfully")
            
            # Get current date for context
            self.current_date = datetime.now().strftime("%B %d, %Y")
            
            # Initialize output filepath
            output_filename = f'strategy_analyses/GGSM-{self.current_date}-DailyAnalysis.md'
            self.output_filepath = os.path.abspath(output_filename)
            
            # Initialize LLM instances for each agent
            self._initialize_llms()
            
            # Track intermediate outputs
            self.intermediate_outputs = {}
            
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
            
            logger.info("Fixed GPSE Crew initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Fixed GPSE Crew: {str(e)}")
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
            max_iter=5,
            verbose=True,
            memory=False,
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
            max_iter=5,
            verbose=True,
            memory=False,
            callbacks=[self._agent_callback]
        )
    
    def communicator(self) -> Agent:
        """Create Strategic Communicator Agent with FIXED tools"""
        config = self.agents_config['communicator']
        logger.debug(f"Creating Communicator with SAVE tools")
        
        # CRITICAL: Give the Communicator the proper tools
        return Agent(
            role=config['role'],
            goal="Save the complete strategic analysis document from the Geo Analyst to disk. Do NOT create a quality report.",
            backstory=config['backstory'] + "\n\nCRITICAL: Your job is to SAVE the analysis, not evaluate it.",
            tools=[self.extract_content_tool, self.save_analysis_tool],  # FIXED: Added tools!
            llm=self.communicator_llm,
            max_iter=3,
            verbose=True,
            memory=False,
            callbacks=[self._agent_callback]
        )
    
    def scout_task(self) -> Task:
        """Create news scouting task from config"""
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
        
        CRITICAL: Use ALL available tools multiple times to gather comprehensive data."""
        
        task = Task(
            description=enhanced_description,
            expected_output=config['expected_output'],
            agent=self.news_scout(),
            callbacks=[self._task_callback]
        )
        
        # Store reference for context passing
        self.news_scout_task_ref = task
        return task
    
    def analysis_task(self) -> Task:
        """Create strategic analysis task from config"""
        config = self.tasks_config['geo_analyst_task']
        
        # Replace date placeholder
        description = config['description'].replace('{current_date}', self.current_date)
        
        task = Task(
            description=description,
            expected_output=config['expected_output'],
            agent=self.geo_analyst(),
            context=[self.news_scout_task_ref],  # Explicit context from news scout
            callbacks=[self._task_callback]
        )
        
        # Store reference for context passing
        self.geo_analyst_task_ref = task
        return task
    
    def communication_task(self) -> Task:
        """Create FIXED communication task"""
        config = self.tasks_config['communicator_task']
        
        # Use the fixed description that explicitly tells Communicator to save the analysis
        description = config['description'].replace('{current_date}', self.current_date)
        
        # Add absolute path reminder
        description += f"\n\nThe absolute file path for saving is: {self.output_filepath}"
        
        task = Task(
            description=description,
            expected_output=config['expected_output'],
            agent=self.communicator(),
            context=[self.news_scout_task_ref, self.geo_analyst_task_ref],  # Full context chain
            output_file=f'strategy_analyses/GGSM-{self.current_date}-DailyAnalysis.md',
            callbacks=[self._task_callback]
        )
        
        return task
    
    def _agent_callback(self, agent_output):
        """Enhanced callback to capture intermediate outputs"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            agent_name = getattr(agent_output, 'agent_name', 'unknown')
            
            logger.info(f"=== AGENT OUTPUT: {agent_name} ===")
            logger.info(f"Output length: {len(str(agent_output))} characters")
            
            # Store in intermediate outputs
            self.intermediate_outputs[agent_name] = str(agent_output)
            
            # Save to debug file
            debug_file = f"debug_outputs/{agent_name}_{timestamp}.txt"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"Agent: {agent_name}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Full Output:\n{str(agent_output)}\n")
            
            logger.info(f"Agent output saved to: {debug_file}")
            
            # Special handling for Geo Analyst output
            if 'analyst' in agent_name.lower():
                analysis_file = f"debug_outputs/geo_analyst_analysis_{timestamp}.md"
                with open(analysis_file, 'w', encoding='utf-8') as f:
                    f.write(str(agent_output))
                logger.info(f"Geo Analyst analysis saved to: {analysis_file}")
                
        except Exception as e:
            logger.error(f"Error in agent callback: {str(e)}")
    
    def _task_callback(self, task_output):
        """Enhanced callback to capture task outputs"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            task_name = getattr(task_output, 'description', 'unknown')[:50]
            
            logger.info(f"=== TASK OUTPUT ===")
            logger.info(f"Task: {task_name}")
            logger.info(f"Output length: {len(str(task_output))} characters")
            
            # Save to debug file
            debug_file = f"debug_outputs/task_{timestamp}.txt"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"Task: {task_name}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Full Output:\n{str(task_output)}\n")
            
            logger.info(f"Task output saved to: {debug_file}")
        except Exception as e:
            logger.error(f"Error in task callback: {str(e)}")
    
    def crew(self) -> Crew:
        """Create and configure the crew with proper task ordering"""
        logger.info("Creating fixed crew with proper context passing")
        
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
        logger.info("Task context chain: News Scout -> Geo Analyst -> Communicator")
        
        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,
            callbacks=[self._crew_callback]
        )
    
    def _crew_callback(self, crew_output):
        """Final callback after crew execution"""
        try:
            logger.info("=== CREW EXECUTION COMPLETE ===")
            logger.info(f"Final output preview: {str(crew_output)[:1000]}...")
            
            # Save all intermediate outputs
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save crew summary
            summary_file = f"debug_outputs/crew_summary_{timestamp}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': timestamp,
                    'final_output': str(crew_output),
                    'intermediate_outputs': self.intermediate_outputs,
                    'expected_file': self.output_filepath
                }, f, indent=2)
            
            logger.info(f"Crew summary saved to: {summary_file}")
            
            # Check if the expected file was created
            if os.path.exists(self.output_filepath):
                logger.info(f"SUCCESS: Strategic analysis saved to {self.output_filepath}")
                with open(self.output_filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    logger.info(f"File size: {len(content)} characters")
                    logger.info(f"File preview: {content[:500]}...")
            else:
                logger.error(f"ERROR: Expected file not found at {self.output_filepath}")
                
        except Exception as e:
            logger.error(f"Error in crew callback: {str(e)}")

def main():
    """Main execution function"""
    output_filepath = None
    
    try:
        print("\n" + "="*60)
        print("GEOPOLITICAL GRAND STRATEGY ENGINE (GPSE)")
        print("FIXED COMMUNICATOR VERSION")
        print("="*60 + "\n")
        
        print(f"Execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Debug outputs will be saved to: debug_outputs/")
        print(f"Logs will be saved to: logs/")
        print("Fix: Communicator will save the actual analysis, not a QA report")
        
        logger.info("Starting Fixed GPSE...")
        
        # Initialize fixed crew
        gpse_crew = GPSECrewFixed()
        
        # Store the output filepath
        output_filepath = gpse_crew.output_filepath
        
        # Log fix status
        logger.info("FIXES APPLIED:")
        logger.info("1. Communicator has save tools")
        logger.info("2. Clear task instructions to save analysis")
        logger.info("3. Proper context passing between agents")
        logger.info("4. Debug saves for intermediate outputs")
        
        # Create crew instance
        crew_instance = gpse_crew.crew()
        
        # Execute crew
        logger.info("Executing Fixed GPSE crew...")
        result = crew_instance.kickoff()
        
        logger.info("Fixed GPSE execution completed!")
        
        # Display results
        print("\n" + "="*50)
        print("FIXED GPSE ANALYSIS COMPLETE")
        print("="*50)
        print(f"\nAnalysis saved to: {output_filepath}")
        print(f"\nDebug outputs saved to: debug_outputs/")
        print(f"Logs saved to: logs/")
        
        # Verify the output file
        if os.path.exists(output_filepath):
            print(f"\n✓ SUCCESS: Strategic analysis file created")
            with open(output_filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check if it's the actual analysis or a QA report
                if "Executive Summary" in content and "Primary Observations" in content:
                    print("✓ VERIFIED: File contains actual strategic analysis")
                else:
                    print("✗ WARNING: File may still be a QA report")
        else:
            print(f"\n✗ ERROR: Expected file not found")
        
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
