#!/usr/bin/env python3
"""
GPSE Direct Runner - Uses LangChain directly without CrewAI
Models: Claude 3.5 Haiku, OpenAI o3, Claude 4 Opus
Token Limit: 30,000 per agent
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import LangChain
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.tools import tool
from langchain.schema import HumanMessage, SystemMessage

# Import Tavily for news
from tavily import TavilyClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enhanced news search tool
@tool("Enhanced News Search")
def enhanced_news_search(query: str) -> str:
    """
    Search for recent news articles using Tavily API with advanced parameters.
    """
    try:
        tavily_key = os.environ.get('TAVILY_API_KEY')
        if not tavily_key:
            return "Error: TAVILY_API_KEY not found"
        
        client = TavilyClient(api_key=tavily_key)
        
        search_params = {
            "query": query,
            "max_results": 10,
            "search_depth": "advanced",
            "topic": "news",
            "days": 3,
            "include_answer": True
        }
        
        logger.info(f"Searching for: {query}")
        results = client.search(**search_params)
        
        # Save raw results for debugging
        debug_dir = Path("debug_outputs")
        debug_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_file = debug_dir / f"raw_news_{timestamp}_{query.replace(' ', '_')[:30]}.json"
        
        import json
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved raw results to: {debug_file}")
        
        if results and 'results' in results:
            formatted_results = [f"Found {len(results['results'])} articles for '{query}':\n"]
            
            if 'answer' in results and results['answer']:
                formatted_results.append(f"AI Summary: {results['answer']}\n")
            
            for i, item in enumerate(results['results'], 1):
                formatted_results.append(f"\n--- Article {i} ---")
                formatted_results.append(f"Title: {item.get('title', 'No title')}")
                formatted_results.append(f"URL: {item.get('url', '')}")
                formatted_results.append(f"Published: {item.get('published_date', '')}")
                formatted_results.append(f"Content: {item.get('content', '')[:500]}...")
                if item.get('score'):
                    formatted_results.append(f"Relevance: {item.get('score', 0.0):.3f}")
            
            return "\n".join(formatted_results)
        else:
            return f"No articles found for: {query}"
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return f"Error: {str(e)}"

class DirectGPSE:
    """Direct GPSE implementation using LangChain without CrewAI"""
    
    def __init__(self):
        """Initialize Direct GPSE"""
        self.current_date = datetime.now().strftime("%B %d, %Y")
        self.output_filename = f'strategy_analyses/GGSM-{self.current_date}-DirectAnalysis.md'
        
        # Initialize LLMs
        self._initialize_llms()
        
        logger.info("Direct GPSE initialized")
    
    def _initialize_llms(self):
        """Initialize LLMs with specific models requested"""
        
        # News Scout: Claude 3.5 Haiku (8K limit per API)
        self.news_scout_llm = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            temperature=0.7,
            max_tokens=8192,  # API limit for this model
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        logger.info("News Scout: Claude 3.5 Haiku (8K tokens - API limit)")
        
        # Analyst: OpenAI with standard API key
        self.analyst_llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            max_tokens=4096  # Use standard token limit
        )
        logger.info("Analyst: GPT-4o")
        
        # Communicator: Claude Opus 4
        self.communicator_llm = ChatAnthropic(
            model="claude-opus-4-20250514",
            temperature=0.5,
            max_tokens=30000,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        logger.info("Communicator: Claude Opus 4 (30K tokens)")
    
    def run_news_scout(self):
        """Run news scouting phase"""
        print("\n=== PHASE 1: NEWS SCOUTING ===")
        
        scout_prompt = f"""You are an elite intelligence analyst conducting comprehensive global geopolitical reconnaissance for {self.current_date}.

Search for and analyze news in these priority areas:
1. Strategic Competition: US-China-Russia dynamics
2. Regional Flashpoints: Taiwan, Ukraine, Middle East
3. Emerging Threats: Cyber, space, AI competition
4. Economic Warfare: Sanctions, trade disputes
5. Non-State Actors: Terrorism, criminal networks
6. Global Governance: UN, international law
7. Technology & Security: Critical infrastructure
8. Climate Security: Resource conflicts

Use the enhanced_news_search tool to find news for each area. Provide comprehensive coverage."""

        # Search for news in key areas
        news_results = []
        search_queries = [
            "US China Russia strategic competition military",
            "Taiwan Ukraine Middle East conflict tensions",
            "cyber attacks AI warfare space militarization",
            "economic sanctions trade war supply chain",
            "terrorism criminal networks non-state actors",
            "UN Security Council international law",
            "critical infrastructure technology security",
            "climate change resource conflicts migration"
        ]
        
        for query in search_queries:
            print(f"\nSearching: {query}")
            result = enhanced_news_search(query)
            news_results.append(result)
        
        # Compile results
        all_news = "\n\n".join(news_results)
        
        # Have the scout analyze the news
        messages = [
            SystemMessage(content=scout_prompt),
            HumanMessage(content=f"Here are the search results:\n\n{all_news}\n\nAnalyze these results and provide a comprehensive intelligence brief.")
        ]
        
        scout_analysis = self.news_scout_llm.invoke(messages)
        print("\nScout Analysis Complete")
        
        return scout_analysis.content
    
    def run_analyst(self, scout_report):
        """Run strategic analysis phase"""
        print("\n=== PHASE 2: STRATEGIC ANALYSIS ===")
        
        analyst_prompt = """You are a senior strategic analyst providing sophisticated multi-dimensional analysis.

Apply this analytical framework:
1. Strategic Environment Assessment
   - Power distribution and shifts
   - Alliance structures
   - Threat landscape evolution

2. Multi-Domain Analysis
   - Military, economic, technological, informational
   - Cross-domain interactions

3. Actor Analysis
   - State actors: capabilities, intentions, constraints
   - Non-state actors: influence, resources, objectives

4. Scenario Development
   - Most likely scenarios (30-90 days)
   - Alternative scenarios
   - Escalation pathways

5. Strategic Implications
   - National security
   - Economic security
   - Alliance implications

Provide deep analysis with probability assessments."""

        messages = [
            SystemMessage(content=analyst_prompt),
            HumanMessage(content=f"Analyze this intelligence report:\n\n{scout_report}")
        ]
        
        analysis = self.analyst_llm.invoke(messages)
        print("\nStrategic Analysis Complete")
        
        return analysis.content
    
    def run_communicator(self, analysis):
        """Create final intelligence product"""
        print("\n=== PHASE 3: STRATEGIC COMMUNICATION ===")
        
        comm_prompt = f"""You are a senior strategic communications specialist creating a professional intelligence assessment.

Create a comprehensive strategic intelligence assessment with:

1. EXECUTIVE SUMMARY (500 words)
   - Key strategic judgments with confidence levels
   - Most significant developments
   - Critical decision points

2. STRATEGIC SITUATION ASSESSMENT
   - Global strategic environment
   - Major power dynamics
   - Regional stability
   - Emerging threats

3. PRIORITY DEVELOPMENTS ANALYSIS
   - Detailed analysis of key events
   - Multi-dimensional impacts
   - Escalation potential

4. SCENARIO ANALYSIS
   - Most likely developments (30-90 days)
   - Alternative scenarios
   - Key indicators to monitor

5. STRATEGIC RECOMMENDATIONS
   - Policy options
   - Risk mitigation
   - Opportunity exploitation

6. INTELLIGENCE GAPS
   - Critical information requirements
   - Collection priorities

Format as a professional intelligence product for {self.current_date}."""

        messages = [
            SystemMessage(content=comm_prompt),
            HumanMessage(content=f"Create a strategic intelligence assessment based on this analysis:\n\n{analysis}")
        ]
        
        final_report = self.communicator_llm.invoke(messages)
        print("\nFinal Report Complete")
        
        return final_report.content
    
    def run(self):
        """Execute the full GPSE pipeline"""
        try:
            # Phase 1: News Scouting
            scout_report = self.run_news_scout()
            
            # Phase 2: Strategic Analysis
            analysis = self.run_analyst(scout_report)
            
            # Phase 3: Final Report
            final_report = self.run_communicator(analysis)
            
            # Save the report
            os.makedirs('strategy_analyses', exist_ok=True)
            with open(self.output_filename, 'w', encoding='utf-8') as f:
                f.write(final_report)
            
            print(f"\n\nReport saved to: {self.output_filename}")
            print(f"Full path: {os.path.abspath(self.output_filename)}")
            
            return final_report
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            raise

def main():
    """Main execution"""
    try:
        print("\n" + "="*70)
        print("GEOPOLITICAL GRAND STRATEGY ENGINE (GPSE)")
        print("DIRECT LANGCHAIN VERSION")
        print("Models: Claude 3.5 Haiku | OpenAI o3 | Claude 4 Opus")
        print("Token Limit: 30,000 per agent")
        print("="*70 + "\n")
        
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check API keys
        if not os.getenv("OPENAI_API_KEY"):
            print("ERROR: OPENAI_API_KEY not found")
            sys.exit(1)
        
        if not os.getenv("TAVILY_API_KEY"):
            print("ERROR: TAVILY_API_KEY not found")
            sys.exit(1)
        
        # Initialize and run
        gpse = DirectGPSE()
        result = gpse.run()
        
        print("\n" + "="*50)
        print("ANALYSIS COMPLETE")
        print("="*50)
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        logger.exception("Full traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()
