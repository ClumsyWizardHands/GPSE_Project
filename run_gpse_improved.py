#!/usr/bin/env python3
"""
GPSE Improved Runner - Enhanced information flow and strategic depth
- News Scout collects raw articles without analysis
- Analyst receives all raw articles for comprehensive analysis
- Communicator has access to both analysis and original sources
"""

import os
import sys
import json
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
        
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved raw results to: {debug_file}")
        
        return results  # Return raw results, not formatted string
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return None

class ImprovedGPSE:
    """Improved GPSE implementation with better information flow"""
    
    def __init__(self):
        """Initialize Improved GPSE"""
        self.current_date = datetime.now().strftime("%B %d, %Y")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_filename = f'strategy_analyses/GGSM-{self.current_date}-ImprovedAnalysis.md'
        self.sources_filename = f'strategy_analyses/GGSM-{self.current_date}-Sources.md'
        
        # Initialize LLMs
        self._initialize_llms()
        
        logger.info("Improved GPSE initialized")
    
    def _initialize_llms(self):
        """Initialize LLMs with specific models requested"""
        
        # News Scout: Claude 3.5 Haiku (NO ANALYSIS - just collection)
        self.news_scout_llm = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            temperature=0.7,
            max_tokens=8192,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        logger.info("News Scout: Claude 3.5 Haiku (Collection only)")
        
        # Analyst: OpenAI o3 (Gets ALL raw articles)
        o3_api_key = os.getenv('OPENAI_API_KEY_O3')
        if not o3_api_key:
            logger.warning("OPENAI_API_KEY_O3 not found, falling back to GPT-4o")
            self.analyst_llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.3,
                max_tokens=4096
            )
            logger.info("Analyst: GPT-4o (Full context analysis)")
        else:
            self.analyst_llm = ChatOpenAI(
                model="o3",
                temperature=1.0,  # o3 only supports default temperature
                max_tokens=4096,
                openai_api_key=o3_api_key
            )
            logger.info("Analyst: OpenAI o3 (Full context analysis)")
        
        # Communicator: Claude Opus 4 (Gets analysis + sources)
        self.communicator_llm = ChatAnthropic(
            model="claude-opus-4-20250514",
            temperature=0.5,
            max_tokens=30000,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        logger.info("Communicator: Claude Opus 4 (Dual access)")
    
    def run_news_scout(self):
        """Run news collection phase - NO ANALYSIS"""
        print("\n=== PHASE 1: NEWS COLLECTION (No Analysis) ===")
        
        # Search for news in key areas
        all_articles = []
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
        
        # Collect all raw articles
        for query in search_queries:
            print(f"\nSearching: {query}")
            results = enhanced_news_search(query)
            
            if results and 'results' in results:
                for article in results['results']:
                    all_articles.append({
                        'query': query,
                        'title': article.get('title', 'No title'),
                        'url': article.get('url', ''),
                        'published_date': article.get('published_date', ''),
                        'content': article.get('content', ''),
                        'score': article.get('score', 0.0),
                        'ai_summary': results.get('answer', '') if results.get('answer') else None
                    })
        
        # Save all articles to markdown file
        self._save_sources_markdown(all_articles)
        
        print(f"\nCollected {len(all_articles)} total articles")
        print(f"Sources saved to: {self.sources_filename}")
        
        return all_articles
    
    def _save_sources_markdown(self, articles):
        """Save all collected articles to a markdown file"""
        os.makedirs('strategy_analyses', exist_ok=True)
        
        with open(self.sources_filename, 'w', encoding='utf-8') as f:
            f.write(f"# GPSE News Sources - {self.current_date}\n\n")
            f.write(f"Total Articles Collected: {len(articles)}\n\n")
            f.write("---\n\n")
            
            # Group by search query
            queries = {}
            for article in articles:
                query = article['query']
                if query not in queries:
                    queries[query] = []
                queries[query].append(article)
            
            # Write articles grouped by query
            for query, query_articles in queries.items():
                f.write(f"## {query}\n\n")
                f.write(f"Articles found: {len(query_articles)}\n\n")
                
                for i, article in enumerate(query_articles, 1):
                    f.write(f"### Article {i}\n")
                    f.write(f"- **Title**: {article['title']}\n")
                    f.write(f"- **URL**: {article['url']}\n")
                    f.write(f"- **Published**: {article['published_date']}\n")
                    f.write(f"- **Relevance Score**: {article['score']:.3f}\n")
                    f.write(f"- **Content**: {article['content'][:1000]}...\n\n")
                
                f.write("---\n\n")
    
    def run_analyst(self, all_articles):
        """Run strategic analysis phase with ALL raw articles"""
        print("\n=== PHASE 2: STRATEGIC ANALYSIS (Full Context) ===")
        
        analyst_prompt = f"""You are a senior strategic analyst providing sophisticated multi-dimensional analysis for {self.current_date}.

You have been provided with {len(all_articles)} raw news articles from the last 48 hours. 
Your task is to analyze ALL of them comprehensively, identifying:

1. CAUSAL RELATIONSHIPS
   - WHY are these events happening now?
   - What strategic goals drive each actor's actions?
   - How do events in different regions interconnect?

2. STRATEGIC CONTEXT
   - Known upcoming events (summits, elections, anniversaries)
   - Seasonal/cyclical factors affecting strategy
   - Domestic political contexts shaping foreign policy

3. COALITION DYNAMICS
   - Which actions are coordinated (e.g., UK + Canada sanctions)?
   - How do alliance obligations constrain or enable actions?
   - What informal cooperation networks are active?

4. SECOND/THIRD-ORDER EFFECTS
   - If X happens, what does it enable for Actor A?
   - What does it constrain for Actor B?
   - How do these cascade into future scenarios?

5. STRATEGIC "WHY" FOR EVERYTHING
   - Why does each development matter for global power balance?
   - Why is the timing significant?
   - What are actors NOT doing by choosing this path?

6. MISSING CONTEXT & GAPS
   - What's NOT being reported that should be?
   - What questions do these articles raise but not answer?
   - Where might deception or misdirection be occurring?

Analyze with maximum specificity. Every claim must reference specific articles.
Identify patterns across ALL articles, not just within topic areas.
Be explicit about confidence levels and evidence quality."""

        # Format articles for analysis
        articles_text = self._format_articles_for_analysis(all_articles)
        
        messages = [
            SystemMessage(content=analyst_prompt),
            HumanMessage(content=f"Analyze these {len(all_articles)} news articles:\n\n{articles_text}")
        ]
        
        analysis = self.analyst_llm.invoke(messages)
        print("\nStrategic Analysis Complete")
        
        return analysis.content
    
    def _format_articles_for_analysis(self, articles):
        """Format articles for analyst consumption"""
        formatted = []
        
        # Group by query for better organization
        queries = {}
        for article in articles:
            query = article['query']
            if query not in queries:
                queries[query] = []
            queries[query].append(article)
        
        for query, query_articles in queries.items():
            formatted.append(f"\n=== {query.upper()} ===")
            formatted.append(f"({len(query_articles)} articles)\n")
            
            for i, article in enumerate(query_articles, 1):
                formatted.append(f"[{i}] {article['title']}")
                formatted.append(f"    Source: {article['url']}")
                formatted.append(f"    Date: {article['published_date']}")
                formatted.append(f"    Content: {article['content']}")
                formatted.append("")
        
        return "\n".join(formatted)
    
    def run_communicator(self, analysis, all_articles):
        """Create final intelligence product with access to both analysis and sources"""
        print("\n=== PHASE 3: STRATEGIC COMMUNICATION (Dual Access) ===")
        
        comm_prompt = f"""You are a senior strategic communications specialist creating a professional intelligence assessment for {self.current_date}.

You have access to:
1. The analyst's strategic assessment
2. All {len(all_articles)} original news articles

Your task is to create a comprehensive strategic intelligence assessment that:

VERIFICATION REQUIREMENTS:
- Fact-check every claim against original sources
- Add missing context the analyst may have overlooked
- Ensure proper source attribution for all claims
- Identify and fill any gaps in the analysis

STRATEGIC DEPTH REQUIREMENTS:
- Explain WHY each development matters strategically
- Show causal chains and interdependencies
- Highlight coalition/alliance dynamics
- Project second and third-order effects

SPECIFIC CONTEXT TO INCLUDE:
- Upcoming NATO summit near The Hague
- Democratic backsliding in key alliance members
- Israel as primary driver of US-Iran tensions
- Any coordinated Western actions (not just unilateral)

FORMAT REQUIREMENTS:
1. EXECUTIVE SUMMARY (500 words)
   - Key strategic judgments with confidence levels
   - Most significant developments with strategic WHY
   - Critical decision points and their implications

2. STRATEGIC SITUATION ASSESSMENT
   - Global power dynamics and their drivers
   - Coalition/alliance developments
   - Cross-domain interactions

3. PRIORITY DEVELOPMENTS ANALYSIS
   - Each development with full context
   - Strategic significance explained
   - Cascading effects mapped

4. SCENARIO ANALYSIS
   - Multiple futures with drivers
   - Key indicators for each path
   - Decision points that shape outcomes

5. STRATEGIC RECOMMENDATIONS
   - Based on evidence and patterns
   - Account for coalition dynamics
   - Consider second-order effects

6. SOURCE ATTRIBUTION
   - Every claim linked to specific articles
   - Confidence levels based on source quality
   - Contradictions explicitly noted"""

        # Provide both analysis and article summary
        articles_summary = self._create_articles_summary(all_articles)
        
        messages = [
            SystemMessage(content=comm_prompt),
            HumanMessage(content=f"""Create a strategic intelligence assessment based on:

ANALYST'S ASSESSMENT:
{analysis}

ORIGINAL SOURCES SUMMARY ({len(all_articles)} articles):
{articles_summary}

Ensure every strategic claim can be traced to specific sources.""")
        ]
        
        final_report = self.communicator_llm.invoke(messages)
        print("\nFinal Report Complete")
        
        return final_report.content
    
    def _create_articles_summary(self, articles):
        """Create a summary of articles for communicator reference"""
        summary = []
        
        # Group by topic
        topics = {}
        for article in articles:
            query = article['query']
            if query not in topics:
                topics[query] = []
            topics[query].append(f"- {article['title']} ({article['published_date']}): {article['content'][:200]}...")
        
        for topic, items in topics.items():
            summary.append(f"\n{topic}:")
            summary.extend(items)
        
        return "\n".join(summary)
    
    def run(self):
        """Execute the improved GPSE pipeline"""
        try:
            # Phase 1: News Collection (No Analysis)
            all_articles = self.run_news_scout()
            
            # Phase 2: Strategic Analysis (Full Context)
            analysis = self.run_analyst(all_articles)
            
            # Phase 3: Final Report (Dual Access)
            final_report = self.run_communicator(analysis, all_articles)
            
            # Save the report
            os.makedirs('strategy_analyses', exist_ok=True)
            with open(self.output_filename, 'w', encoding='utf-8') as f:
                f.write(final_report)
            
            print(f"\n\nReport saved to: {self.output_filename}")
            print(f"Sources saved to: {self.sources_filename}")
            print(f"Full paths:")
            print(f"  Report: {os.path.abspath(self.output_filename)}")
            print(f"  Sources: {os.path.abspath(self.sources_filename)}")
            
            return final_report
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            raise

def main():
    """Main execution"""
    try:
        print("\n" + "="*70)
        print("GEOPOLITICAL GRAND STRATEGY ENGINE (GPSE)")
        print("IMPROVED VERSION - Enhanced Information Flow")
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
        gpse = ImprovedGPSE()
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
