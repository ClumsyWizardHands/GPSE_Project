"""
GPSE Main Crew Implementation - NO MEMORY VERSION
This version runs without ChromaDB to isolate permission issues
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any
from crewai import Agent, Task, Crew, Process

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import tools
from gpse_tools_comprehensive import (
    enhanced_news_search,
    fetch_news_from_url,
    aggregate_geopolitical_news,
    query_strategy_database
)

class GPSECrew:
    """GPSE Crew without memory for testing purposes"""
    
    def __init__(self):
        """Initialize the GPSE Crew"""
        try:
            # Initialize shared tools
            self.news_tool = enhanced_news_search
            self.url_fetch_tool = fetch_news_from_url
            self.aggregator_tool = aggregate_geopolitical_news
            self.database_tool = query_strategy_database
            
            logger.info("Tools initialized successfully")
            
            # Get current date for context
            self.current_date = datetime.now().strftime("%B %d, %Y")
            
            # Initialize LLM configuration
            self.llm_config = self._get_llm_config()
            
            logger.info("GPSE Crew initialized - NO MEMORY VERSION")
            
        except Exception as e:
            logger.error(f"Failed to initialize GPSE Crew: {str(e)}")
            raise
    
    def _get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        logger.info("Using OpenAI models")
        return {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 4000
        }
    
    def news_scout(self) -> Agent:
        """Create News Scout Agent"""
        return Agent(
            role='Geopolitical News Scout',
            goal='Identify and analyze breaking geopolitical developments with focus on China-US-Russia dynamics',
            backstory="""You are an elite intelligence analyst specializing in real-time geopolitical 
            monitoring. Your expertise lies in identifying significant developments in international 
            relations, military movements, economic policies, and diplomatic initiatives. You have 
            deep knowledge of global power dynamics and can quickly assess the strategic importance 
            of emerging events.""",
            tools=[self.news_tool, self.aggregator_tool, self.url_fetch_tool],
            llm_config=self.llm_config,
            max_iter=3,
            verbose=True
        )
    
    def geo_analyst(self) -> Agent:
        """Create Geopolitical Analyst Agent"""
        return Agent(
            role='Strategic Geopolitical Analyst',
            goal='Provide deep strategic analysis of global power dynamics and their implications',
            backstory="""You are a senior strategic analyst with decades of experience in international 
            relations and military strategy. You specialize in analyzing the complex interplay between 
            China, the United States, and Russia, understanding their strategic doctrines, capabilities, 
            and long-term objectives. Your analysis integrates military, economic, technological, and 
            diplomatic dimensions to provide comprehensive strategic assessments.""",
            tools=[self.database_tool, self.news_tool],
            llm_config=self.llm_config,
            max_iter=3,
            verbose=True
        )
    
    def communicator(self) -> Agent:
        """Create Strategic Communicator Agent"""
        return Agent(
            role='Strategic Communications Specialist',
            goal='Transform complex geopolitical analysis into clear, actionable intelligence briefs',
            backstory="""You are an expert strategic communicator who specializes in distilling complex 
            geopolitical analysis into clear, actionable intelligence products. You understand how to 
            present information to decision-makers, highlighting key insights, strategic implications, 
            and actionable recommendations. Your communication is precise, structured, and focused on 
            strategic value.""",
            tools=[],
            llm_config=self.llm_config,
            max_iter=2,
            verbose=True
        )
    
    def scout_task(self) -> Task:
        """Create news scouting task"""
        return Task(
            description=f"""Conduct comprehensive geopolitical news reconnaissance for {self.current_date}.
            
            Focus Areas:
            1. China-US-Russia strategic developments
            2. Military movements and defense initiatives
            3. Economic policies and trade dynamics
            4. Diplomatic engagements and tensions
            5. Technology competition and security concerns
            
            Requirements:
            - Use the news search and aggregator tools to find REAL current news
            - Identify 5-7 most significant developments from actual sources
            - Verify information from multiple sources
            - Assess immediate strategic implications
            - Flag any breaking or urgent developments
            
            Output Format:
            - Executive Summary (2-3 sentences)
            - Key Developments (bullet points with actual sources and URLs)
            - Strategic Implications
            - Confidence Assessment""",
            expected_output="Comprehensive geopolitical news brief with verified developments and initial strategic assessment",
            agent=self.news_scout()
        )
    
    def analysis_task(self) -> Task:
        """Create strategic analysis task"""
        return Task(
            description=f"""Conduct deep strategic analysis of the geopolitical developments identified.
            
            Analysis Framework:
            1. Strategic Context: How do these developments fit into broader power competition?
            2. Actor Analysis: Motivations, capabilities, and constraints of key players
            3. Trend Identification: What patterns are emerging or accelerating?
            4. Risk Assessment: What are the escalation risks and strategic vulnerabilities?
            5. Forecast: Likely developments in next 30-90 days
            
            Requirements:
            - Use the database tool to find relevant historical context
            - Apply strategic frameworks (deterrence theory, balance of power, etc.)
            - Consider multiple scenarios and their probabilities
            - Identify strategic opportunities and threats
            - Provide evidence-based assessments
            
            Include historical context where relevant but focus on current implications.""",
            expected_output="Comprehensive strategic analysis with scenarios, risks, and actionable insights",
            agent=self.geo_analyst()
        )
    
    def communication_task(self) -> Task:
        """Create strategic communication task"""
        return Task(
            description=f"""Create a strategic intelligence brief for senior decision-makers.
            
            Brief Requirements:
            1. Executive Summary: Key findings and recommendations (1 paragraph)
            2. Strategic Situation: Current state of great power competition
            3. Critical Developments: Most important changes and their implications
            4. Strategic Assessment: Risks, opportunities, and trending indicators
            5. Recommendations: Specific, actionable strategic options
            
            Style Guidelines:
            - Clear, concise, and direct language
            - Highlight actionable intelligence
            - Use strategic terminology appropriately
            - Include confidence levels for assessments
            
            Format as a professional intelligence product suitable for high-level briefing.""",
            expected_output="Professional strategic intelligence brief with clear findings and actionable recommendations",
            agent=self.communicator(),
            output_file=f'strategy_analyses/GGSM-{self.current_date}-DailyAnalysis.md'
        )
    
    def crew(self) -> Crew:
        """Create and configure the crew"""
        logger.info("Creating crew without memory")
        
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
            memory=False  # Explicitly disable memory
        )

def main():
    """Main execution function"""
    try:
        logger.info("Starting GPSE without Memory...")
        
        # Create output directory
        os.makedirs('strategy_analyses', exist_ok=True)
        
        # Initialize crew
        gpse_crew = GPSECrew()
        
        # Create crew instance
        crew_instance = gpse_crew.crew()
        
        # Execute crew
        logger.info("Executing GPSE crew...")
        result = crew_instance.kickoff()
        
        logger.info("GPSE execution completed successfully!")
        logger.info(f"Results: {result}")
        
        # Display results
        print("\n" + "="*50)
        print("GPSE ANALYSIS COMPLETE")
        print("="*50)
        print(f"\nAnalysis saved to: strategy_analyses/GGSM-{datetime.now().strftime('%B %d, %Y')}-DailyAnalysis.md")
        print("\nKey Findings:")
        print("-" * 50)
        if result:
            print(result)
        
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        logger.exception("Full traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()
