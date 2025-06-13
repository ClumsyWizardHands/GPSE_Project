"""
GPSE Main Crew - Deep Analysis Version
Uses advanced AI models: Claude 3.5 Haiku, OpenAI o3, Claude 4 Opus
"""

# Apply Windows-specific fixes
try:
    import pysqlite3
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    print("Applied pysqlite3-binary fix for Windows")
except ImportError:
    print("Note: pysqlite3-binary not available - using standard sqlite3")
    pass  # Continue without pysqlite3

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Apply Windows-specific fixes BEFORE importing CrewAI/ChromaDB
os.environ["CREWAI_STORAGE_DIR"] = r"C:\gpse_data"
os.environ["CHROMA_SEGMENT_MANAGER_IMPL"] = "local"
os.environ["SQLITE_TMPDIR"] = os.environ.get("TEMP", r"C:\temp")

# Ensure the storage directory exists
storage_path = Path(os.environ["CREWAI_STORAGE_DIR"])
storage_path.mkdir(parents=True, exist_ok=True)
print(f"Storage directory ready: {storage_path}")

# Now import CrewAI
from crewai import Agent, Task, Crew, Process

# Import LangChain LLM modules
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Import tools
from gpse_tools import (
    enhanced_news_search,
    fetch_news_from_url,
    aggregate_geopolitical_news,
    query_strategy_database
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class GPSECrewDeep:
    """GPSE Crew with Deep Analysis using Advanced AI Models"""
    
    def __init__(self):
        """Initialize the GPSE Crew with Advanced Models"""
        try:
            # Initialize shared tools
            self.news_tool = enhanced_news_search
            self.url_fetch_tool = fetch_news_from_url
            self.aggregator_tool = aggregate_geopolitical_news
            self.database_tool = query_strategy_database
            
            logger.info("Tools initialized successfully")
            
            # Get current date for context
            self.current_date = datetime.now().strftime("%B %d, %Y")
            
            # Initialize output filepath for deep analysis
            output_filename = f'strategy_analyses/GGSM-{self.current_date}-DeepAnalysis.md'
            self.output_filepath = os.path.abspath(output_filename)
            
            # Initialize LLM instances for each agent
            self._initialize_llms()
            
            logger.info("GPSE Crew initialized with Deep Analysis Models")
            
        except Exception as e:
            logger.error(f"Failed to initialize GPSE Crew: {str(e)}")
            raise
    
    def _initialize_llms(self):
        """Initialize different LLM configurations for each agent with advanced models"""
        
        # News Scout: Claude 3.5 Haiku for fast, efficient news processing
        try:
            self.news_scout_llm = ChatAnthropic(
                model="claude-3-5-haiku-20241022",
                temperature=0.7,
                max_tokens=30000,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            logger.info("News Scout LLM: Claude 3.5 Haiku (30K tokens)")
        except Exception as e:
            logger.warning(f"Claude 3.5 Haiku failed, using fallback: {e}")
            self.news_scout_llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=30000,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            logger.info("News Scout LLM: GPT-4o Mini fallback (30K tokens)")
        
        # Geopolitical Analyst: OpenAI o3 for advanced reasoning
        try:
            self.geo_analyst_llm = ChatOpenAI(
                model="o3",
                temperature=0.3,  # Lower temperature for analytical precision
                max_tokens=30000,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            logger.info("Geopolitical Analyst LLM: OpenAI o3 (30K tokens)")
        except Exception as e:
            logger.warning(f"OpenAI o3 failed, using GPT-4o fallback: {e}")
            self.geo_analyst_llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.3,
                max_tokens=30000,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            logger.info("Geopolitical Analyst LLM: GPT-4o fallback (30K tokens)")
        
        # Communicator: Claude 4 Opus for advanced communication
        try:
            self.communicator_llm = ChatAnthropic(
                model="claude-4-opus",
                temperature=0.5,
                max_tokens=30000,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            logger.info("Communicator LLM: Claude 4 Opus (30K tokens)")
        except Exception as e:
            logger.warning(f"Claude 4 Opus failed, using Claude 3.5 Sonnet fallback: {e}")
            self.communicator_llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0.5,
                max_tokens=30000,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            logger.info("Communicator LLM: Claude 3.5 Sonnet fallback (30K tokens)")
    
    def news_scout(self) -> Agent:
        """Create News Scout Agent"""
        return Agent(
            role='Global Geopolitical News Scout',
            goal='Identify and analyze breaking geopolitical developments from all regions and power centers worldwide',
            backstory="""You are an elite intelligence analyst specializing in real-time global 
            geopolitical monitoring. Your expertise spans all continents and regions - from major 
            powers like the US, China, Russia, and EU to critical regions like the Middle East, 
            South Asia, Africa, Latin America, and Southeast Asia. You track developments in 
            international relations, military movements, economic policies, diplomatic initiatives, 
            conflicts, and emerging security challenges wherever they occur. You understand that 
            geopolitical significance isn't limited to great powers but includes regional powers, 
            non-state actors, and emerging threats.""",
            tools=[self.news_tool, self.aggregator_tool, self.url_fetch_tool],
            llm=self.news_scout_llm,  # Use Claude 3.5 Haiku
            max_iter=3,
            verbose=True,
            memory=True  # Enable memory
        )
    
    def geo_analyst(self) -> Agent:
        """Create Geopolitical Analyst Agent"""
        return Agent(
            role='Comprehensive Strategic Geopolitical Analyst',
            goal='Provide deep strategic analysis of global developments across all regions and their interconnected implications',
            backstory="""You are a senior strategic analyst with decades of experience in international 
            relations and global security. Your expertise covers the entire geopolitical landscape - 
            from traditional great power competition to regional conflicts, emerging security challenges, 
            non-state actors, cyber threats, climate-driven instability, and economic warfare. You 
            analyze how events in one region affect others, understanding the complex web of alliances, 
            rivalries, and interdependencies that shape global politics. You're equally versed in 
            analyzing developments in the Middle East, Africa, South Asia, Europe, Latin America, 
            and the Asia-Pacific, recognizing that today's multipolar world requires comprehensive 
            global awareness.""",
            tools=[self.database_tool, self.news_tool],
            llm=self.geo_analyst_llm,  # Use OpenAI o3
            max_iter=3,
            verbose=True,
            memory=True  # Enable memory
        )
    
    def communicator(self) -> Agent:
        """Create Strategic Communicator Agent"""
        return Agent(
            role='Strategic Communications Specialist',
            goal='Transform complex global geopolitical analysis into clear, comprehensive intelligence briefs',
            backstory="""You are an expert strategic communicator who specializes in distilling complex 
            geopolitical analysis into clear, actionable intelligence products. You ensure comprehensive 
            coverage of global developments, not just focusing on major powers but giving appropriate 
            attention to all significant regional developments, emerging threats, and non-traditional 
            security challenges. You understand that decision-makers need a complete global picture, 
            including developments in Africa, the Middle East, South Asia, Latin America, and other 
            regions that may have strategic implications.""",
            tools=[],
            llm=self.communicator_llm,  # Use Claude 4 Opus
            max_iter=2,
            verbose=True,
            memory=True  # Enable memory
        )
    
    def scout_task(self) -> Task:
        """Create news scouting task"""
        return Task(
            description=f"""Conduct comprehensive global geopolitical news reconnaissance for {self.current_date}.
            
            Focus Areas (ALL regions must be covered):
            1. Major Power Dynamics: US, China, Russia, EU relations and actions
            2. Middle East: Israel-Palestine, Iran, Saudi Arabia, Syria, Yemen
            3. Europe: NATO, Ukraine conflict, EU politics, energy security
            4. Asia-Pacific: Taiwan, South China Sea, Korea, Japan, ASEAN
            5. South Asia: India-Pakistan, Afghanistan, regional tensions
            6. Africa: Conflicts, coups, resource competition, great power involvement
            7. Latin America: Political changes, US relations, China's influence
            8. Global Security: Cyber attacks, terrorism, nuclear proliferation
            9. Economic Warfare: Sanctions, trade wars, currency conflicts
            10. Emerging Challenges: Climate conflicts, migration, pandemics
            
            Requirements:
            - Use the news aggregator tool with diverse regional focus areas
            - Ensure balanced coverage - do NOT over-focus on any single region
            - Identify 10-15 most significant developments globally
            - Include at least 2-3 developments from regions outside US-China-Russia
            - Verify information from multiple sources
            - Assess immediate strategic implications for each region
            
            Output Format:
            - Executive Summary (covering ALL major regions)
            - Key Developments by Region (with sources and URLs)
            - Global Strategic Implications
            - Emerging Patterns Across Regions""",
            expected_output="Comprehensive global news brief with balanced regional coverage and strategic assessment",
            agent=self.news_scout()
        )
    
    def analysis_task(self) -> Task:
        """Create strategic analysis task"""
        return Task(
            description=f"""Conduct deep strategic analysis of ALL geopolitical developments identified globally.
            
            Analysis Framework:
            1. Regional Analysis: Examine developments in EACH region reported
            2. Cross-Regional Impacts: How do events in one region affect others?
            3. Power Dynamics: Analyze not just US-China-Russia but also regional powers
            4. Non-State Actors: Consider terrorist groups, corporations, criminal networks
            5. Emerging Threats: Identify new patterns beyond traditional state competition
            6. Global Trends: What patterns connect different regional developments?
            
            Requirements:
            - Analyze ALL regions where significant events occurred
            - Do NOT default to only discussing US-China-Russia dynamics
            - Consider second and third-order effects across regions
            - Include analysis of regional powers (India, Brazil, Turkey, etc.)
            - Apply diverse analytical frameworks beyond just great power competition
            - Identify risks and opportunities in each region
            
            Ensure comprehensive global coverage in your analysis.""",
            expected_output="Comprehensive strategic analysis covering all global regions with interconnected insights",
            agent=self.geo_analyst()
        )
    
    def communication_task(self) -> Task:
        """Create strategic communication task"""
        # Use the output filepath that was already initialized
        output_filename = f'strategy_analyses/GGSM-{self.current_date}-DeepAnalysis.md'
        
        return Task(
            description=f"""Create a comprehensive global strategic intelligence brief for senior decision-makers.
            
            Brief Requirements:
            1. Executive Summary: Global overview touching ALL major regions
            2. Regional Assessments: Dedicated sections for each region with developments
               - Americas (North and South)
               - Europe and Russia
               - Middle East and North Africa
               - Sub-Saharan Africa
               - South and Central Asia
               - East Asia and Pacific
            3. Cross-Regional Analysis: How developments interconnect globally
            4. Emerging Global Threats: Beyond traditional state competition
            5. Strategic Recommendations: Region-specific and global actions
            
            Style Guidelines:
            - Ensure balanced coverage - no region should dominate
            - If more content exists for one region, explicitly note gaps in others
            - Highlight non-traditional security challenges
            - Include confidence levels for assessments
            - Make recommendations for each region discussed
            
            Format as a professional intelligence product with comprehensive global coverage.
            
            IMPORTANT: After saving the document, include the absolute file path in your response.""",
            expected_output=f"Professional global strategic intelligence brief with balanced regional coverage saved to {self.output_filepath}",
            agent=self.communicator(),
            output_file=output_filename
        )
    
    def crew(self) -> Crew:
        """Create and configure the crew"""
        logger.info("Creating crew with memory enabled and advanced AI models")
        
        return Crew(
            agents=[
                self.news_scout(),
                self.geo_analyst(),
                self.communicator()
            ],
            tasks=[
                self.scout_task(),
                self.analysis_task(),
                self.communication_task()
            ],
            process=Process.sequential,
            verbose=True,
            memory=True  # Enable memory with Windows fixes
        )

def main():
    """Main execution function"""
    output_filepath = None
    
    try:
        print("\n" + "="*70)
        print("GEOPOLITICAL GRAND STRATEGY ENGINE (GPSE)")
        print("DEEP ANALYSIS VERSION")
        print("Advanced AI Models: Claude 3.5 Haiku | OpenAI o3 | Claude 4 Opus")
        print("Token Limit: 30,000 per agent")
        print("="*70 + "\n")
        
        print(f"Execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Storage directory: {os.environ['CREWAI_STORAGE_DIR']}")
        
        logger.info("Starting GPSE with Deep Analysis Models...")
        
        # Create output directory
        os.makedirs('strategy_analyses', exist_ok=True)
        
        # Initialize crew
        gpse_crew = GPSECrewDeep()
        
        # Store the output filepath
        output_filepath = gpse_crew.output_filepath
        
        # Create crew instance
        crew_instance = gpse_crew.crew()
        
        # Execute crew
        logger.info("Executing GPSE crew with advanced AI models...")
        result = crew_instance.kickoff()
        
        logger.info("GPSE Deep Analysis execution completed successfully!")
        logger.info(f"Results: {result}")
        
        # Display results
        print("\n" + "="*50)
        print("GPSE DEEP ANALYSIS COMPLETE")
        print("="*50)
        print(f"\nAnalysis saved to: strategy_analyses/GGSM-{datetime.now().strftime('%B %d, %Y')}-DeepAnalysis.md")
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
        
        if "permission" in str(e).lower() or "chromadb" in str(e).lower():
            print("\nChromaDB Error Detected!")
            print("Try these solutions:")
            print("1. Run as Administrator (one time)")
            print("2. Check antivirus isn't blocking")
            print("3. Use no-memory version if issue persists")
        
        logger.exception("Full traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()
