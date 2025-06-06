"""
GPSE Main Crew Execution Script - Windows ChromaDB Working Version
Combines Windows fixes with the correct function imports from the no-memory version
"""

# CRITICAL: Apply pysqlite3-binary fix BEFORE any other imports
try:
    import pysqlite3
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    print("✓ Applied pysqlite3-binary fix for Windows")
except ImportError:
    print("⚠️ pysqlite3-binary not available - using standard sqlite3")

import os
import warnings
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Apply Windows-specific fixes BEFORE importing CrewAI/ChromaDB
# Use short path to avoid MAX_PATH issues
os.environ["CREWAI_STORAGE_DIR"] = r"C:\gpse_data"
os.environ["CHROMA_SEGMENT_MANAGER_IMPL"] = "local"
os.environ["SQLITE_TMPDIR"] = os.environ.get("TEMP", r"C:\temp")

# Ensure the storage directory exists
storage_path = Path(os.environ["CREWAI_STORAGE_DIR"])
storage_path.mkdir(parents=True, exist_ok=True)
print(f"✓ Storage directory ready: {storage_path}")

# Now import CrewAI and other dependencies
from crewai import Agent, Task, Crew, Process

# Import tools using the correct function imports from gpse_tools_comprehensive
from gpse_tools_comprehensive import (
    enhanced_news_search,
    fetch_news_from_url,
    aggregate_geopolitical_news,
    query_strategy_database,
    save_strategic_document,
    archive_to_chromadb
)

# Suppress warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Custom LLM configuration
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o"

def create_gpse_crew():
    """Create the GPSE crew with all agents and tasks"""
    
    # Initialize tools
    news_tool = enhanced_news_search
    url_fetch_tool = fetch_news_from_url
    aggregator_tool = aggregate_geopolitical_news
    database_tool = query_strategy_database
    save_tool = save_strategic_document
    archive_tool = archive_to_chromadb
    
    # Create agents with memory enabled
    news_scout = Agent(
        role='Information Curation Specialist',
        goal='Gather and curate the most relevant global political news and events from the past 24-48 hours',
        backstory="""You are an expert information curator specializing in global political intelligence. 
        Your expertise lies in identifying significant geopolitical events, filtering out noise, and 
        presenting organized, relevant information that impacts global strategic dynamics. You excel at 
        distinguishing between routine news and events with strategic implications.""",
        tools=[news_tool, aggregator_tool, url_fetch_tool],
        verbose=True,
        memory=True,  # Enable agent memory
        allow_delegation=False
    )
    
    geo_analyst = Agent(
        role='Lead Strategy Analyst',
        goal='Synthesize current events with historical strategic analyses to produce comprehensive geopolitical assessments',
        backstory="""You are a senior geopolitical strategist with decades of experience analyzing global power 
        dynamics. Your strength lies in connecting current events to historical patterns, understanding the 
        motivations of state and non-state actors, and identifying emerging strategic trends. You think in 
        terms of capabilities, intentions, and the complex interplay of economic, military, and diplomatic power. 
        You always ground your analysis in historical context retrieved from the strategy database.""",
        tools=[database_tool],
        verbose=True,
        memory=True,  # Enable agent memory
        allow_delegation=False
    )
    
    communicator = Agent(
        role='Communications & Archival Lead',
        goal='Transform strategic analyses into clear, structured documents and maintain the strategy knowledge base',
        backstory="""You are a strategic communications expert who excels at translating complex geopolitical 
        analysis into clear, actionable intelligence documents. You understand the importance of consistency, 
        clarity, and proper archival for building a long-term strategic knowledge base. You ensure all analyses 
        are properly formatted, saved, and indexed for future reference.""",
        tools=[save_tool, archive_tool],
        verbose=True,
        memory=True,  # Enable agent memory
        allow_delegation=False
    )
    
    # Create output directory
    os.makedirs('strategy_analyses', exist_ok=True)
    
    # Get current date for output file
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Create tasks
    news_gathering_task = Task(
        description=f"""Gather comprehensive global political news from the last 24-48 hours.
        
        Current Date: {current_date}
        
        Requirements:
        1. Query multiple news sources for diverse perspectives using the news tools
        2. Focus on events with strategic implications:
           - Military movements or conflicts
           - Diplomatic breakthroughs or breakdowns
           - Economic sanctions or trade agreements
           - Leadership changes in key nations
           - Strategic technology developments
        3. Organize findings by region and significance
        4. Include source attribution for all information
        5. Filter out routine or non-strategic news
        
        Output a structured summary with:
        - Executive overview of key developments
        - Detailed findings organized by region
        - Assessment of strategic significance for each item
        - Clear source citations with URLs""",
        agent=news_scout,
        expected_output="Comprehensive structured news summary with strategic implications clearly identified"
    )
    
    analysis_task = Task(
        description=f"""Produce a comprehensive geopolitical strategic analysis that synthesizes current events 
        with historical patterns and strategic context.
        
        Current Date: {current_date}
        
        Requirements:
        1. MANDATORY: Query the strategy database for relevant historical analyses using query_strategy_database tool
        2. Connect current events to historical patterns and past analyses
        3. Analyze from multiple perspectives:
           - Major power competition (US, China, Russia, EU)
           - Regional power dynamics
           - Non-state actor influences
           - Economic and technological factors
        4. Identify:
           - Emerging strategic trends
           - Potential future scenarios
           - Key uncertainties and indicators to watch
           - Strategic implications for different actors
        5. Ground all analysis in evidence and historical precedent
        
        Structure your analysis with:
        - Executive Summary
        - Analysis of key actors and their strategic positions
        - Scenario analysis (minimum 3 scenarios)
        - Strategic recommendations or implications
        - Indicators to monitor""",
        agent=geo_analyst,
        expected_output="Comprehensive strategic analysis document with clear reasoning and historical grounding"
    )
    
    documentation_task = Task(
        description=f"""Format the strategic analysis into a professional document and update the knowledge base.
        
        Current Date: {current_date}
        
        Requirements:
        1. Create a properly formatted strategic analysis document following the GPSE template
        2. Ensure clear section headers and logical flow
        3. Include metadata:
           - Date: {current_date}
           - Key topics and regions covered
           - Referenced historical analyses
        4. Save the document using save_strategic_document tool
        5. Archive the analysis in ChromaDB using archive_to_chromadb tool with appropriate chunks:
           - Executive summary
           - Individual country/actor analyses
           - Scenario analyses
           - Strategic implications
        6. Verify successful storage and retrieval
        
        Quality checks:
        - Ensure all sections are complete
        - Verify factual accuracy
        - Check that historical references are properly cited
        - Confirm successful database storage""",
        agent=communicator,
        expected_output="Professional strategic analysis document saved and properly archived in the knowledge base",
        output_file=f'strategy_analyses/GGSM-{current_date}-DailyAnalysis.md'
    )
    
    # Create and return crew with memory enabled
    crew = Crew(
        agents=[news_scout, geo_analyst, communicator],
        tasks=[news_gathering_task, analysis_task, documentation_task],
        process=Process.sequential,
        verbose=True,
        memory=True  # Enable crew memory
    )
    
    return crew

def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("GEOPOLITICAL GRAND STRATEGY ENGINE (GPSE)")
    print("Windows ChromaDB Working Version with Memory")
    print("="*60 + "\n")
    
    print(f"Execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Storage directory: {os.environ['CREWAI_STORAGE_DIR']}")
    
    try:
        # Create and execute the crew
        print("\nInitializing GPSE crew with Windows fixes and memory...")
        crew = create_gpse_crew()
        
        print("\nStarting strategic analysis workflow...")
        print("This process will:")
        print("1. Gather recent global political news")
        print("2. Analyze events with historical context") 
        print("3. Produce strategic assessment document")
        print("\n" + "-"*60 + "\n")
        
        result = crew.kickoff()
        
        print("\n" + "="*60)
        print("EXECUTION COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nAnalysis saved to: strategy_analyses/GGSM-{datetime.now().strftime('%B %d, %Y')}-DailyAnalysis.md")
        print("\nFinal Output:")
        print("-"*60)
        print(result)
        
    except Exception as e:
        print("\n" + "="*60)
        print("ERROR DURING EXECUTION")
        print("="*60)
        print(f"Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. If ChromaDB error: Run as Administrator (one time)")
        print("2. If still failing: Use no-memory version")
        print("3. Check antivirus isn't blocking file access")
        
        import traceback
        print("\nFull error trace:")
        traceback.print_exc()

if __name__ == "__main__":
    main()
