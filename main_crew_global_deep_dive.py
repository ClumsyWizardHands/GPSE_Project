"""
GPSE Main Crew - Global Coverage Deep Dive Version
Produces both executive brief AND comprehensive regional deep-dive analyses
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
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

# Import tools
from gpse_tools_comprehensive import (
    enhanced_news_search,
    fetch_news_from_url,
    aggregate_geopolitical_news,
    query_strategy_database
)

# Import the enhanced communicator with multi-file capabilities
from communicator_agent_enhanced import (
    MultiFileWriterTool,
    EnhancedStrategyDBUpdateTool,
    create_enhanced_communicator_agent
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class GPSECrewDeepDive:
    """GPSE Crew with Global Coverage and Deep Dive Analysis"""
    
    def __init__(self):
        """Initialize the GPSE Deep Dive Crew"""
        try:
            # Initialize shared tools
            self.news_tool = enhanced_news_search
            self.url_fetch_tool = fetch_news_from_url
            self.aggregator_tool = aggregate_geopolitical_news
            self.database_tool = query_strategy_database
            
            # Initialize enhanced communicator tools
            self.multi_writer_tool = MultiFileWriterTool()
            self.enhanced_db_tool = EnhancedStrategyDBUpdateTool()
            
            logger.info("Tools initialized successfully")
            
            # Get current date for context
            self.current_date = datetime.now().strftime("%B %d, %Y")
            
            # Initialize LLM instances for each agent
            self._initialize_llms()
            
            logger.info("GPSE Deep Dive Crew initialized with Global Coverage")
            
        except Exception as e:
            logger.error(f"Failed to initialize GPSE Deep Dive Crew: {str(e)}")
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
        
        # Geopolitical Analyst: o1-preview for maximum reasoning capability
        self.geo_analyst_llm = ChatOpenAI(
            model="o1-preview",
            temperature=0.7,
            max_tokens=25000,  # Substantially increased for comprehensive analysis
            api_key=os.getenv("OPENAI_API_KEY")
        )
        logger.info("Geopolitical Analyst LLM: o1-preview (advanced reasoning)")
        
        # Communicator: GPT-4o Mini with multi-file capabilities
        self.communicator_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=8000,  # Increased for multiple outputs
            api_key=os.getenv("OPENAI_API_KEY")
        )
        logger.info("Communicator LLM: GPT-4o Mini (multi-file output)")
    
    def news_scout(self) -> Agent:
        """Create News Scout Agent"""
        return Agent(
            role='Global Geopolitical News Scout',
            goal='Identify and analyze breaking geopolitical developments from all regions with full source attribution',
            backstory="""You are an elite intelligence analyst specializing in real-time global 
            geopolitical monitoring with rigorous source verification. You apply the comprehensive 
            analytical protocols including:
            - Complete source verification with bias assessment (AllSides/MBFC standards)
            - Precise UTC timestamps for all events
            - Contradiction documentation when sources conflict
            - Temporal anomaly detection
            - Friction tagging (narrative, infrastructure, enforcement)
            - Actor event continuity tracking
            You track developments across ALL regions - Americas, Europe, Middle East, Africa, 
            South Asia, East Asia, and emerging threats.""",
            tools=[self.news_tool, self.aggregator_tool, self.url_fetch_tool],
            llm=self.news_scout_llm,
            max_iter=5,  # Increased for comprehensive coverage
            verbose=True,
            memory=True
        )
    
    def geo_analyst(self) -> Agent:
        """Create Enhanced Geopolitical Analyst Agent"""
        return Agent(
            role='Comprehensive Strategic Geopolitical Analyst',
            goal='Produce exhaustively detailed strategic assessments using all analytical frameworks',
            backstory="""You are a world-class intelligence analyst who produces both executive 
            summaries AND deep analytical dives. You apply ALL analytical protocols including:
            
            - Relational Game Theory (RGT) micro-protocols
            - Creative inference frameworks
            - Counterfactual and pretextual modeling  
            - Adversarial stress simulations
            - Cascade effect modeling
            - Strategic blind spot analysis
            
            For each region, you provide:
            - Complete temporal event sequences
            - Actor behavior modeling with game theory payoff matrices
            - Strategic inference chains with evidence
            - Probability-weighted scenarios
            - Cross-regional interdependencies
            - Intelligence gaps and collection priorities
            
            You NEVER compress analysis - you provide FULL depth for every region.""",
            tools=[self.database_tool, self.news_tool],
            llm=self.geo_analyst_llm,
            max_iter=15,  # Increased to allow comprehensive analysis completion
            verbose=True,
            memory=True
        )
    
    def communicator(self) -> Agent:
        """Create Enhanced Strategic Communicator Agent with Deep Dive capabilities"""
        return Agent(
            role='Strategic Communications Officer - Deep Analysis Specialist',
            goal='Transform analyses into BOTH executive brief AND multiple detailed regional deep dives',
            backstory="""You are a master strategic communicator who creates comprehensive intelligence 
            products at multiple levels of detail. You produce:
            
            1. EXECUTIVE BRIEF: Concise summary for senior decision-makers
            2. REGIONAL DEEP DIVES: Exhaustive analyses for each region including:
               - Complete source verification chains
               - Full temporal sequences with friction analysis
               - Detailed actor modeling with game theory
               - Strategic inference sections
               - Counterfactual scenarios with probabilities
               - Cross-regional cascade effects
               - Intelligence gaps and priorities
            
            You ensure EVERY analytical insight from the geo_analyst is preserved in the deep dives.
            Nothing is compressed or summarized - the full analytical depth is maintained.""",
            tools=[self.multi_writer_tool, self.enhanced_db_tool],
            llm=self.communicator_llm,
            max_iter=5,
            verbose=True,
            memory=True
        )
    
    def scout_task(self) -> Task:
        """Create enhanced news scouting task"""
        return Task(
            description=f"""Conduct comprehensive global geopolitical news reconnaissance for {self.current_date}.
            
            Apply ALL source verification protocols:
            - Domain authority and editorial standards check
            - Political bias classification (AllSides scale)  
            - Factual reporting rating (MBFC scale)
            - Primary source verification
            - UTC timestamps for all events
            - Contradiction documentation
            - Temporal anomaly detection
            - Friction tagging
            
            Focus Areas (ALL must be covered with equal depth):
            1. Americas: US, Canada, Mexico, Brazil, Venezuela, regional dynamics
            2. Europe: EU, UK, NATO, Russia-Ukraine, energy security
            3. Middle East: Israel-Palestine, Iran, Saudi Arabia, Syria, Yemen
            4. Africa: Sahel conflicts, Ethiopia, resource competition, great power involvement
            5. South Asia: India-Pakistan, Afghanistan, Bangladesh, Sri Lanka
            6. East Asia: China, Taiwan, Korea, Japan, ASEAN dynamics
            7. Central Asia: Kazakhstan, strategic corridors, Russia-China influence
            8. Global Security: Cyber, terrorism, nuclear, space, climate conflicts
            9. Economic Warfare: Sanctions, trade wars, currency manipulation
            10. Non-State Actors: Terrorist groups, criminal networks, corporations
            
            Output must include full source attribution for EVERY claim.""",
            expected_output="Comprehensive global news brief with complete source verification and balanced coverage",
            agent=self.news_scout()
        )
    
    def analysis_task(self) -> Task:
        """Create enhanced strategic analysis task"""
        return Task(
            description=f"""Produce EXHAUSTIVE strategic analysis for ALL regions using EVERY analytical framework.
            
            MANDATORY SECTIONS FOR EACH REGION:
            
            1. TEMPORAL ANALYSIS
               - Complete event timeline with UTC stamps
               - Temporal anomalies and delays
               - Pattern acceleration/deceleration
            
            2. ACTOR BEHAVIOR MODELING
               - Game theory payoff matrices
               - Objective functions and constraints
               - Decision tree analysis
               - Reputational risk calculations
            
            3. STRATEGIC INFERENCE
               - Creative connections between events
               - Hidden alignments and preparations
               - Absent expected actions
               - Timing synchronicities
            
            4. COUNTERFACTUAL SCENARIOS
               - Multiple futures with probabilities
               - Trigger events and escalation ladders
               - Key indicators to watch
            
            5. CASCADE EFFECTS
               - Cross-regional impacts
               - Second and third-order effects
               - System instability points
            
            6. INTELLIGENCE GAPS
               - Critical missing information
               - Collection priorities
               - Analytical uncertainties
            
            DO NOT COMPRESS - provide FULL analytical depth for EVERY region.
            Each regional analysis should be 2000-3000 words minimum.""",
            expected_output="Exhaustive multi-region strategic analysis with complete analytical frameworks applied",
            agent=self.geo_analyst()
        )
    
    def communication_task(self) -> Task:
        """Create enhanced strategic communication task for deep dives"""
        return Task(
            description=f"""Create BOTH executive brief AND comprehensive deep-dive analyses.
            
            DELIVERABLES:
            
            1. EXECUTIVE BRIEF (1-2 pages)
               - High-level global overview
               - Key findings from each region
               - Strategic recommendations
               - Save as: GGSM-{self.current_date}-DailyAnalysis.md
            
            2. REGIONAL DEEP DIVES (5-10 pages each)
               Create separate detailed analysis files for:
               - Americas (North and South)
               - Europe and Russia  
               - Middle East and North Africa
               - Sub-Saharan Africa
               - South and Central Asia
               - East Asia and Pacific
               - Global Threats and Non-State Actors
            
            Each deep dive MUST include:
               - Complete source verification chains with bias assessments
               - Full temporal event sequences with UTC timestamps
               - Detailed actor behavior modeling using game theory
               - Strategic inference sections with evidence trails
               - Counterfactual scenarios with probability assessments
               - Cross-regional cascade effects
               - Intelligence gaps and collection priorities
            
            Use the multi_writer_tool to create all files.
            
            Then use the enhanced_db_tool to update ChromaDB with all documents.
            
            Ensure NO analytical insights are lost between the analyst's work and the final documents.""",
            expected_output="Executive brief plus 7 regional deep-dive analyses saved as separate files",
            agent=self.communicator()
        )
    
    def crew(self) -> Crew:
        """Create and configure the crew"""
        logger.info("Creating deep dive crew with enhanced memory")
        
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
            memory=True
        )

def main():
    """Main execution function"""
    try:
        print("\n" + "="*60)
        print("GEOPOLITICAL GRAND STRATEGY ENGINE (GPSE)")
        print("Deep Dive Analysis Version - Executive Brief + Regional Deep Dives")
        print("="*60 + "\n")
        
        print(f"Execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Storage directory: {os.environ['CREWAI_STORAGE_DIR']}")
        
        logger.info("Starting GPSE Deep Dive Analysis...")
        
        # Create output directory
        os.makedirs('strategy_analyses', exist_ok=True)
        
        # Initialize crew
        gpse_crew = GPSECrewDeepDive()
        
        # Create crew instance
        crew_instance = gpse_crew.crew()
        
        # Execute crew
        logger.info("Executing GPSE deep dive crew...")
        result = crew_instance.kickoff()
        
        logger.info("GPSE deep dive execution completed successfully!")
        logger.info(f"Results: {result}")
        
        # Display results
        print("\n" + "="*50)
        print("GPSE DEEP DIVE ANALYSIS COMPLETE")
        print("="*50)
        print(f"\nAnalysis files created in: strategy_analyses/")
        print("\nFiles Generated:")
        print("- Executive Brief: GGSM-[Date]-DailyAnalysis.md")
        print("- Regional Deep Dives: GGSM-[Date]-DeepDive-[Region].md")
        print("- Analysis Index: GGSM-[Date]-Index.md")
        print("\nAll analyses added to ChromaDB for future reference")
        
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
