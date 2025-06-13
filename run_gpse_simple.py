#!/usr/bin/env python3
"""
GPSE Simple Runner - Basic version that works with current dependencies
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import CrewAI
from crewai import Agent, Task, Crew, Process

# Import LangChain
from langchain_openai import ChatOpenAI
from langchain.tools import tool

# Import Tavily for news
from tavily import TavilyClient
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simple news search tool
@tool("News Search")
def search_news(query: str) -> str:
    """
    Search for recent news articles using Tavily API.
    Provide a search query to find relevant news articles.
    """
    try:
        tavily_key = os.environ.get('TAVILY_API_KEY')
        if not tavily_key:
            return "Error: TAVILY_API_KEY not found in environment variables"
        
        client = TavilyClient(api_key=tavily_key)
        
        # Search parameters
        search_params = {
            "query": query,
            "max_results": 5,
            "search_depth": "advanced",
            "topic": "news",
            "days": 2  # Last 48 hours
        }
        
        logger.info(f"Searching for: {query}")
        results = client.search(**search_params)
        
        if results and 'results' in results:
            formatted_results = [f"Found {len(results['results'])} news articles for '{query}':\n"]
            
            for i, item in enumerate(results['results'], 1):
                formatted_results.append(f"\n--- Article {i} ---")
                formatted_results.append(f"Title: {item.get('title', 'No title')}")
                formatted_results.append(f"URL: {item.get('url', '')}")
                formatted_results.append(f"Published: {item.get('published_date', '')}")
                formatted_results.append(f"Summary: {item.get('content', '')[:300]}...")
            
            return "\n".join(formatted_results)
        else:
            return f"No news articles found for query: {query}"
            
    except Exception as e:
        logger.error(f"Error searching news: {str(e)}")
        return f"Error searching for news: {str(e)}"

class SimpleGPSE:
    """Simple GPSE implementation"""
    
    def __init__(self):
        """Initialize the Simple GPSE"""
        self.current_date = datetime.now().strftime("%B %d, %Y")
        self.output_filename = f'strategy_analyses/GGSM-{self.current_date}-SimpleAnalysis.md'
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        logger.info("Simple GPSE initialized")
    
    def news_scout(self) -> Agent:
        """Create News Scout Agent"""
        return Agent(
            role='Global News Scout',
            goal='Find and analyze recent geopolitical news from around the world',
            backstory="""You are a news analyst who specializes in finding and summarizing 
            important geopolitical developments. You search for news about international 
            relations, conflicts, diplomatic developments, and major political events 
            that could impact global stability.""",
            tools=[search_news],
            llm=self.llm,
            verbose=True
        )
    
    def analyst(self) -> Agent:
        """Create Strategic Analyst Agent"""
        return Agent(
            role='Strategic Analyst',
            goal='Analyze geopolitical developments and their strategic implications',
            backstory="""You are a strategic analyst with expertise in international 
            relations and geopolitics. You analyze news events to understand their 
            broader implications for global stability, regional power dynamics, and 
            strategic relationships between nations.""",
            tools=[],
            llm=self.llm,
            verbose=True
        )
    
    def scout_task(self) -> Task:
        """Create news scouting task"""
        return Task(
            description=f"""Search for and summarize the most important geopolitical news for {self.current_date}.
            
            Focus on these key areas:
            1. International conflicts and tensions
            2. Diplomatic developments
            3. Military movements or announcements
            4. Economic sanctions or trade disputes
            5. Major political changes in key countries
            
            Search for news in each of these areas and provide a comprehensive summary 
            of the most significant developments.""",
            expected_output="Comprehensive summary of recent geopolitical news with sources",
            agent=self.news_scout()
        )
    
    def analysis_task(self) -> Task:
        """Create analysis task"""
        return Task(
            description=f"""Analyze the geopolitical developments identified by the news scout.
            
            Provide strategic analysis covering:
            1. Immediate implications of each development
            2. Potential escalation scenarios
            3. Impact on regional stability
            4. Effects on major power relationships
            5. Recommendations for monitoring
            
            Create a professional strategic assessment that decision-makers can use.""",
            expected_output=f"Strategic analysis report saved to {self.output_filename}",
            agent=self.analyst(),
            output_file=self.output_filename
        )
    
    def crew(self) -> Crew:
        """Create and configure the crew"""
        return Crew(
            agents=[
                self.news_scout(),
                self.analyst()
            ],
            tasks=[
                self.scout_task(),
                self.analysis_task()
            ],
            process=Process.sequential,
            verbose=True
        )

def main():
    """Main execution function"""
    try:
        print("\n" + "="*60)
        print("GEOPOLITICAL GRAND STRATEGY ENGINE (GPSE)")
        print("Simple Version")
        print("="*60 + "\n")
        
        print(f"Execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check API keys
        if not os.getenv("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY not found in environment variables")
            sys.exit(1)
        
        if not os.getenv("TAVILY_API_KEY"):
            print("Error: TAVILY_API_KEY not found in environment variables")
            sys.exit(1)
        
        logger.info("Starting Simple GPSE...")
        
        # Create output directory
        os.makedirs('strategy_analyses', exist_ok=True)
        
        # Initialize GPSE
        gpse = SimpleGPSE()
        
        # Create crew instance
        crew_instance = gpse.crew()
        
        # Execute crew
        logger.info("Executing GPSE crew...")
        result = crew_instance.kickoff()
        
        logger.info("GPSE execution completed successfully!")
        
        # Display results
        print("\n" + "="*50)
        print("GPSE ANALYSIS COMPLETE")
        print("="*50)
        print(f"\nAnalysis saved to: {gpse.output_filename}")
        print("\nKey Findings:")
        print("-" * 50)
        if result:
            print(result)
        
        print(f"\nOutput file: {os.path.abspath(gpse.output_filename)}")
        
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
