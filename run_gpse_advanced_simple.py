#!/usr/bin/env python3
"""
GPSE Advanced Simple Runner - Uses advanced AI models with simple architecture
Models: Claude 3.5 Haiku, OpenAI o3/GPT-4o, Claude 4 Opus/Claude 3.5 Sonnet
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

# Import CrewAI
from crewai import Agent, Task, Crew, Process

# Import LangChain
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
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

# Enhanced news search tool
@tool("Enhanced News Search")
def enhanced_news_search(query: str) -> str:
    """
    Search for recent news articles using Tavily API with advanced parameters.
    Provide a search query to find relevant news articles.
    """
    try:
        tavily_key = os.environ.get('TAVILY_API_KEY')
        if not tavily_key:
            return "Error: TAVILY_API_KEY not found in environment variables"
        
        client = TavilyClient(api_key=tavily_key)
        
        # Enhanced search parameters for deep analysis
        search_params = {
            "query": query,
            "max_results": 10,  # More results for comprehensive analysis
            "search_depth": "advanced",
            "topic": "news",
            "days": 3,  # Last 72 hours
            "include_answer": True
        }
        
        logger.info(f"Deep searching for: {query}")
        results = client.search(**search_params)
        
        if results and 'results' in results:
            formatted_results = [f"Found {len(results['results'])} news articles for '{query}':\n"]
            
            if 'answer' in results and results['answer']:
                formatted_results.append(f"AI Summary: {results['answer']}\n")
            
            for i, item in enumerate(results['results'], 1):
                formatted_results.append(f"\n--- Article {i} ---")
                formatted_results.append(f"Title: {item.get('title', 'No title')}")
                formatted_results.append(f"URL: {item.get('url', '')}")
                formatted_results.append(f"Published: {item.get('published_date', '')}")
                formatted_results.append(f"Content: {item.get('content', '')[:500]}...")
                if item.get('score'):
                    formatted_results.append(f"Relevance Score: {item.get('score', 0.0):.3f}")
            
            return "\n".join(formatted_results)
        else:
            return f"No news articles found for query: {query}"
            
    except Exception as e:
        logger.error(f"Error searching news: {str(e)}")
        return f"Error searching for news: {str(e)}"

class AdvancedGPSE:
    """Advanced GPSE implementation with high-end AI models"""
    
    def __init__(self):
        """Initialize the Advanced GPSE"""
        self.current_date = datetime.now().strftime("%B %d, %Y")
        self.output_filename = f'strategy_analyses/GGSM-{self.current_date}-AdvancedAnalysis.md'
        
        # Initialize advanced LLMs with 30K tokens
        self._initialize_llms()
        
        logger.info("Advanced GPSE initialized with high-end models")
    
    def _initialize_llms(self):
        """Initialize different LLM configurations for each agent"""
        
        # News Scout: Claude 3.5 Haiku for fast, efficient news processing
        try:
            self.news_scout_llm = ChatAnthropic(
                model="claude-3-5-haiku-20241022",
                temperature=0.7,
                max_tokens=30000,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            logger.info("News Scout: Claude 3.5 Haiku (30K tokens)")
        except Exception as e:
            logger.warning(f"Claude 3.5 Haiku unavailable: {e}")
            self.news_scout_llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=30000,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            logger.info("News Scout: GPT-4o Mini fallback (30K tokens)")
        
        # Geopolitical Analyst: OpenAI o3 for advanced reasoning
        try:
            self.geo_analyst_llm = ChatOpenAI(
                model="o3",
                temperature=0.3,  # Lower temperature for analytical precision
                max_tokens=30000,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            logger.info("Geopolitical Analyst: OpenAI o3 (30K tokens)")
        except Exception as e:
            logger.warning(f"OpenAI o3 unavailable: {e}")
            self.geo_analyst_llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.3,
                max_tokens=30000,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            logger.info("Geopolitical Analyst: GPT-4o fallback (30K tokens)")
        
        # Communicator: Claude 4 Opus for advanced communication
        try:
            self.communicator_llm = ChatAnthropic(
                model="claude-4-opus",
                temperature=0.5,
                max_tokens=30000,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            logger.info("Communicator: Claude 4 Opus (30K tokens)")
        except Exception as e:
            logger.warning(f"Claude 4 Opus unavailable: {e}")
            try:
                self.communicator_llm = ChatAnthropic(
                    model="claude-3-5-sonnet-20241022",
                    temperature=0.5,
                    max_tokens=30000,
                    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
                )
                logger.info("Communicator: Claude 3.5 Sonnet fallback (30K tokens)")
            except:
                self.communicator_llm = ChatOpenAI(
                    model="gpt-4o",
                    temperature=0.5,
                    max_tokens=30000,
                    openai_api_key=os.getenv("OPENAI_API_KEY")
                )
                logger.info("Communicator: GPT-4o fallback (30K tokens)")
    
    def news_scout(self) -> Agent:
        """Create News Scout Agent with advanced capabilities"""
        return Agent(
            role='Elite Global Intelligence Scout',
            goal='Conduct comprehensive deep-dive reconnaissance of global geopolitical developments',
            backstory="""You are an elite intelligence analyst with access to advanced search capabilities 
            and real-time global monitoring systems. Your expertise spans all continents, regions, and 
            geopolitical domains. You specialize in identifying emerging patterns, hidden connections, 
            and early warning indicators across multiple information streams. You have deep knowledge 
            of international relations, military strategy, economic warfare, and hybrid threats.""",
            tools=[enhanced_news_search],
            llm=self.news_scout_llm,
            verbose=True
        )
    
    def analyst(self) -> Agent:
        """Create Strategic Analyst Agent with advanced reasoning"""
        return Agent(
            role='Senior Strategic Geopolitical Analyst',
            goal='Provide sophisticated multi-dimensional analysis of global developments',
            backstory="""You are a senior strategic analyst with decades of experience in international 
            relations, military strategy, and global security. Your analytical framework incorporates 
            multiple theoretical perspectives including realism, liberalism, constructivism, and critical 
            theory. You excel at systems thinking, understanding complex interdependencies, and identifying 
            second and third-order effects. You analyze developments across all regions - from great powers 
            to regional conflicts, emerging threats, and non-state actors.""",
            tools=[],
            llm=self.geo_analyst_llm,
            verbose=True
        )
    
    def communicator(self) -> Agent:
        """Create Strategic Communicator Agent with advanced synthesis"""
        return Agent(
            role='Senior Strategic Communications Specialist',
            goal='Transform complex geopolitical analysis into sophisticated intelligence products',
            backstory="""You are a senior strategic communications specialist who works at the highest 
            levels of government and international organizations. You excel at synthesizing complex, 
            multi-faceted analysis into clear, compelling, and actionable intelligence products. You 
            understand that decision-makers need comprehensive global coverage, including developments 
            in all regions and domains - military, economic, technological, and informational.""",
            tools=[],
            llm=self.communicator_llm,
            verbose=True
        )
    
    def scout_task(self) -> Task:
        """Create enhanced news scouting task"""
        return Task(
            description=f"""Conduct comprehensive global geopolitical intelligence collection for {self.current_date}.
            
            PRIORITY INTELLIGENCE REQUIREMENTS:
            1. Strategic Competition: US-China-Russia dynamics, alliance structures
            2. Regional Flashpoints: Taiwan, Ukraine, Middle East, Korean Peninsula
            3. Emerging Threats: Cyber warfare, space militarization, AI competition
            4. Economic Warfare: Sanctions, trade disputes, supply chain vulnerabilities
            5. Hybrid Threats: Information warfare, election interference, gray zone operations
            6. Non-State Actors: Terrorist organizations, criminal networks
            7. Global Governance: UN Security Council, international law
            8. Technology & Security: Critical infrastructure, semiconductors
            9. Climate Security: Resource conflicts, migration pressures
            10. Domestic-International Nexus: Elections, political instability
            
            Search comprehensively for news on each priority area. Provide detailed coverage with 
            multiple sources for each development. Include confidence assessments.""",
            expected_output="Comprehensive intelligence collection report with multi-source verification",
            agent=self.news_scout()
        )
    
    def analysis_task(self) -> Task:
        """Create sophisticated analysis task"""
        return Task(
            description=f"""Conduct sophisticated strategic analysis of all intelligence collected.
            
            ANALYTICAL FRAMEWORK:
            1. Strategic Environment Assessment
               - Power distribution and shifts
               - Alliance structures and effectiveness
               - Threat landscape evolution
            
            2. Multi-Domain Analysis
               - Land, sea, air, space, cyber, information domains
               - Cross-domain interactions and vulnerabilities
            
            3. Actor Analysis
               - State actors: capabilities, intentions, constraints
               - Non-state actors: influence, resources, objectives
               - Decision-making calculus and red lines
            
            4. Scenario Development
               - Most likely scenarios (30-90 days) with probability assessments
               - Alternative scenarios and wild cards
               - Escalation pathways and off-ramps
            
            5. Strategic Implications
               - National security implications
               - Economic security implications
               - Alliance and partnership implications
               - Technology competition impacts
            
            Apply multiple analytical techniques including:
            - Game theory modeling
            - Systems analysis
            - Historical analogies
            - Trend extrapolation
            - Counterfactual reasoning
            
            Challenge assumptions and consider contrarian viewpoints.""",
            expected_output="Sophisticated strategic analysis with scenario development and probability assessments",
            agent=self.analyst()
        )
    
    def communication_task(self) -> Task:
        """Create strategic communication task"""
        return Task(
            description=f"""Create a sophisticated strategic intelligence assessment for senior decision-makers.
            
            PRODUCT REQUIREMENTS:
            
            1. EXECUTIVE SUMMARY (500 words)
               - Key strategic judgments with confidence levels
               - Most significant developments and implications
               - Critical decision points
               - Red lines and triggers
            
            2. STRATEGIC SITUATION ASSESSMENT
               - Global strategic environment overview
               - Major power dynamics and competition
               - Regional stability assessments
               - Emerging threat landscape
               - Technology competition status
            
            3. PRIORITY DEVELOPMENTS ANALYSIS
               - Detailed analysis of most significant events
               - Multi-dimensional impact assessment
               - Stakeholder analysis
               - Escalation potential
               - Historical context and precedents
            
            4. SCENARIO ANALYSIS
               - Most likely developments (30-90 days)
               - Alternative scenarios with probabilities
               - Wild card events and black swans
               - Strategic implications of each scenario
               - Key indicators to monitor
            
            5. STRATEGIC RECOMMENDATIONS
               - Policy options with pros/cons
               - Risk mitigation strategies
               - Opportunity exploitation
               - Alliance considerations
               - Resource allocation priorities
            
            6. INTELLIGENCE GAPS
               - Critical information requirements
               - Collection priorities
               - Analytical uncertainties
            
            Format as professional intelligence product with clear structure and actionable insights.""",
            expected_output=f"Professional strategic intelligence assessment saved to {self.output_filename}",
            agent=self.communicator(),
            output_file=self.output_filename
        )
    
    def crew(self) -> Crew:
        """Create and configure the crew"""
        return Crew(
            agents=[
                self.news_scout(),
                self.analyst(),
                self.communicator()
            ],
            tasks=[
                self.scout_task(),
                self.analysis_task(),
                self.communication_task()
            ],
            process=Process.sequential,
            verbose=True
        )

def main():
    """Main execution function"""
    try:
        print("\n" + "="*70)
        print("GEOPOLITICAL GRAND STRATEGY ENGINE (GPSE)")
        print("ADVANCED ANALYSIS VERSION")
        print("AI Models: Claude 3.5 Haiku | OpenAI o3 | Claude 4 Opus")
        print("Token Limit: 30,000 per agent")
        print("="*70 + "\n")
        
        print(f"Execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check API keys
        required_keys = ["OPENAI_API_KEY", "TAVILY_API_KEY", "ANTHROPIC_API_KEY"]
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        
        if missing_keys:
            print(f"\nWARNING: Missing API keys: {', '.join(missing_keys)}")
            print("Some models will use fallbacks")
        
        logger.info("Starting Advanced GPSE...")
        
        # Create output directory
        os.makedirs('strategy_analyses', exist_ok=True)
        
        # Initialize GPSE
        print("\nInitializing advanced AI models...")
        gpse = AdvancedGPSE()
        
        # Create crew instance
        print("\nCreating AI agent crew...")
        crew_instance = gpse.crew()
        
        # Execute crew
        print("\nExecuting advanced geopolitical analysis...")
        print("This may take several minutes...\n")
        
        result = crew_instance.kickoff()
        
        logger.info("Advanced GPSE execution completed successfully!")
        
        # Display results
        print("\n" + "="*50)
        print("ADVANCED ANALYSIS COMPLETE")
        print("="*50)
        print(f"\nAnalysis saved to: {gpse.output_filename}")
        
        # Also save the result manually if output_file didn't work
        if result and not os.path.exists(gpse.output_filename):
            with open(gpse.output_filename, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"Results manually saved to: {gpse.output_filename}")
        
        print(f"\nFull path: {os.path.abspath(gpse.output_filename)}")
        
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        print("\n" + "="*60)
        print("ERROR DURING EXECUTION")
        print("="*60)
        print(f"Error: {str(e)}")
        
        if "pydantic" in str(e).lower():
            print("\nPydantic version conflict detected!")
            print("This is a known issue when running Windows-developed code on macOS")
            print("The simple version (run_gpse_simple.py) should work better")
        
        logger.exception("Full traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()
