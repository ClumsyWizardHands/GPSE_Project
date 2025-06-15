#!/usr/bin/env python3
"""
GPSE Enhanced Memory Runner - Multi-Source News + Breaking Event Detection
- News Scout uses both Tavily and WorldNewsAPI for comprehensive coverage
- Detects breaking events and generates adaptive searches
- Analyst queries ChromaDB for relevant past analyses
- Full memory integration with historical context
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any, Tuple

# Load environment variables
load_dotenv()

class TemporalEventParser:
    """Parse temporal context from articles"""
    
    def __init__(self):
        self.past_markers = ['after', 'following', 'in the aftermath', 'has struck', 'attacked', 'bombed', 'destroyed', 'killed', 'wounded', 'hit', 'struck']
        self.future_markers = ['will', 'preparing', 'plans to', 'threatens to', 'could', 'may', 'potential', 'expected to', 'likely to']
        self.present_markers = ['is attacking', 'currently', 'ongoing', 'underway', 'continues to', 'is striking']
    
    def classify_event_temporality(self, title, content):
        """Classify if event is past, present, or future"""
        text = (title + " " + content[:500]).lower()
        
        past_score = sum(1 for marker in self.past_markers if marker in text)
        future_score = sum(1 for marker in self.future_markers if marker in text)
        present_score = sum(1 for marker in self.present_markers if marker in text)
        
        if past_score > future_score and past_score > present_score:
            return "PAST"
        elif future_score > past_score and future_score > present_score:
            return "FUTURE"
        else:
            return "PRESENT/ONGOING"

# Import LangChain
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.tools import tool
from langchain.schema import HumanMessage, SystemMessage

# Import Tavily for news
from tavily import TavilyClient

# Import ChromaDB manager
from db_manager_enhanced import ChromaDBManager
from gpse_tools import pathway_extractor
from schemas import StrategicPathway
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorldNewsAPI:
    """WorldNewsAPI client for breaking news coverage"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.worldnewsapi.com"
    
    def search_news(self, query: str, language: str = "en", 
                   earliest_publish_date: str = None, 
                   latest_publish_date: str = None,
                   number: int = 10) -> Dict[str, Any]:
        """Search for news articles using WorldNewsAPI"""
        
        # Set date range to last 3 days if not specified
        if not earliest_publish_date:
            earliest_date = datetime.now() - timedelta(days=3)
            earliest_publish_date = earliest_date.strftime("%Y-%m-%d")
        
        if not latest_publish_date:
            latest_publish_date = datetime.now().strftime("%Y-%m-%d")
        
        params = {
            "text": query,
            "language": language,
            "earliest-publish-date": earliest_publish_date,
            "latest-publish-date": latest_publish_date,
            "number": number,
            "sort": "publish-time",
            "sort-direction": "DESC",
            "api-key": self.api_key
        }
        
        try:
            response = requests.get(f"{self.base_url}/search-news", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"WorldNewsAPI error: {str(e)}")
            return {"news": []}

# Enhanced news search tool combining multiple sources
@tool("Multi-Source News Search")
def multi_source_news_search(query: str) -> Dict[str, Any]:
    """
    Search for news using both Tavily and WorldNewsAPI for comprehensive coverage
    """
    results = {
        "query": query,
        "tavily_results": [],
        "worldnews_results": [],
        "combined_articles": []
    }
    
    # Tavily search
    try:
        tavily_key = os.environ.get('TAVILY_API_KEY')
        if tavily_key:
            client = TavilyClient(api_key=tavily_key)
            
            search_params = {
                "query": query,
                "max_results": 10,
                "search_depth": "advanced",
                "topic": "news",
                "days": 3,
                "include_answer": True
            }
            
            logger.info(f"Tavily searching for: {query}")
            tavily_results = client.search(**search_params)
            results["tavily_results"] = tavily_results.get("results", [])
    except Exception as e:
        logger.error(f"Tavily error: {str(e)}")
    
    # WorldNewsAPI search
    try:
        worldnews_key = os.environ.get('WORLDNEWS_API_KEY')
        if worldnews_key:
            worldnews_client = WorldNewsAPI(worldnews_key)
            logger.info(f"WorldNewsAPI searching for: {query}")
            worldnews_results = worldnews_client.search_news(query)
            results["worldnews_results"] = worldnews_results.get("news", [])
    except Exception as e:
        logger.error(f"WorldNewsAPI error: {str(e)}")
    
    # Combine and deduplicate results
    seen_urls = set()
    
    # Process Tavily results
    for article in results["tavily_results"]:
        url = article.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            results["combined_articles"].append({
                'source': 'tavily',
                'title': article.get('title', 'No title'),
                'url': url,
                'published_date': article.get('published_date', ''),
                'content': article.get('content', ''),
                'score': article.get('score', 0.0)
            })
    
    # Process WorldNews results
    for article in results["worldnews_results"]:
        url = article.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            results["combined_articles"].append({
                'source': 'worldnews',
                'title': article.get('title', 'No title'),
                'url': url,
                'published_date': article.get('publish_date', ''),
                'content': article.get('text', ''),
                'author': article.get('author', ''),
                'language': article.get('language', 'en')
            })
    
    logger.info(f"Combined search found {len(results['combined_articles'])} unique articles")
    return results

class BreakingEventDetector:
    """Detects breaking geopolitical events from initial news collection"""
    
    def __init__(self, llm, current_date):
        self.llm = llm
        self.current_date = current_date
        self.crisis_keywords = {
            'military': ['airstrike', 'missile', 'attack', 'invasion', 'bombing', 'strike', 'military operation'],
            'political': ['coup', 'assassination', 'overthrow', 'revolution', 'resignation', 'impeachment'],
            'diplomatic': ['sanctions', 'embassy', 'expelled', 'recalled', 'severed ties', 'ultimatum'],
            'economic': ['collapse', 'default', 'crash', 'crisis', 'embargo', 'blockade'],
            'security': ['nuclear', 'chemical weapons', 'terrorism', 'hostage', 'hijacking']
        }
    
    def detect_breaking_events(self, articles: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Analyze articles for breaking events and generate additional search queries
        Returns: (breaking_events, additional_queries)
        """
        
        # First pass: keyword detection
        potential_events = []
        for article in articles:
            title = article.get('title', '').lower()
            content = article.get('content', '')[:500].lower()
            
            event_indicators = []
            for category, keywords in self.crisis_keywords.items():
                for keyword in keywords:
                    if keyword in title or keyword in content:
                        event_indicators.append((category, keyword))
            
            if event_indicators:
                potential_events.append({
                    'article': article,
                    'indicators': event_indicators
                })
        
        if not potential_events:
            return [], []
        
        # Second pass: LLM analysis for breaking events
        event_summaries = []
        for event in potential_events[:10]:  # Analyze top 10 potential events
            event_summaries.append(f"Title: {event['article']['title']}\nIndicators: {event['indicators']}")
        
        prompt = f"""Analyze these news items for BREAKING geopolitical events.

CRITICAL: Determine the TEMPORAL STATUS of each event:
- ALREADY HAPPENED: Use past tense (e.g., "Israel struck Iran")
- HAPPENING NOW: Use present tense (e.g., "Israel is striking Iran")
- ANTICIPATED/PLANNED: Use future tense (e.g., "Israel preparing to strike Iran")

Look for temporal markers:
- Past: "after", "following", "in aftermath of", "struck", "attacked"
- Future: "preparing", "plans to", "will", "threatens to"
- Present: "ongoing", "currently", "is attacking"

Today's date is {self.current_date}. Articles dated today describing events are about TODAY's events.

{chr(10).join(event_summaries)}

Format your response with CORRECT TEMPORAL CONTEXT:
BREAKING EVENT 1: [Description with CORRECT TENSE]
TEMPORAL STATUS: [PAST/PRESENT/FUTURE]
IMPACT LEVEL: [HIGH/MEDIUM]
ADDITIONAL QUERIES:
- [Query 1]
- [Query 2]

Only include events that are genuinely breaking and high-impact."""

        messages = [
            SystemMessage(content="You are a geopolitical analyst identifying breaking news events."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Parse response for additional queries
        additional_queries = []
        lines = response.content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('- ') and i > 0 and 'ADDITIONAL QUERIES' in lines[i-1]:
                query = line.strip()[2:]
                if query:
                    additional_queries.append(query)
        
        # Extract breaking events
        breaking_events = []
        current_event = {}
        for line in lines:
            if line.startswith('BREAKING EVENT'):
                if current_event:
                    breaking_events.append(current_event)
                current_event = {'description': line}
            elif line.startswith('IMPACT LEVEL:'):
                current_event['impact'] = line.split(':')[1].strip()
        
        if current_event:
            breaking_events.append(current_event)
        
        return breaking_events, additional_queries[:5]  # Limit to 5 additional queries

class EnhancedGPSEWithMemory:
    """Enhanced GPSE with multi-source news and breaking event detection"""
    
    def __init__(self):
        """Initialize Enhanced GPSE with Memory"""
        self.current_date = datetime.now().strftime("%B %d, %Y")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_filename = f'strategy_analyses/GGSM-{self.current_date}-EnhancedMemoryAnalysis.md'
        self.sources_filename = f'strategy_analyses/GGSM-{self.current_date}-EnhancedMemorySources.md'
        
        # Initialize ChromaDB manager
        self.db_manager = ChromaDBManager(db_path='./strategy_db_chroma')
        logger.info("ChromaDB manager initialized")
        
        # Initialize LLMs
        self._initialize_llms()
        
        # Initialize breaking event detector
        self.event_detector = BreakingEventDetector(self.news_scout_llm, self.current_date)
        
        # Initialize temporal parser
        self.temporal_parser = TemporalEventParser()
        
        logger.info("Enhanced GPSE with Memory initialized")
    
    def _initialize_llms(self):
        """Initialize LLMs with specific models requested"""
        
        # News Scout: Claude 3.5 Haiku (Collection + Breaking Event Detection)
        self.news_scout_llm = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            temperature=0.7,
            max_tokens=8192,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        logger.info("News Scout: Claude 3.5 Haiku (Multi-source collection)")
        
        # Analyst: OpenAI o3 (Gets ALL raw articles + historical context)
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
                max_completion_tokens=4096,
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
    
    def query_historical_context(self, topics):
        """Query ChromaDB for relevant historical analyses"""
        print("\n=== QUERYING HISTORICAL CONTEXT ===")
        
        historical_context = []
        
        # Query for each major topic area
        for topic in topics:
            print(f"\nQuerying historical data for: {topic}")
            results = self.db_manager.query_db(topic, n_results=3)
            
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'][0] else {}
                    distance = results['distances'][0][i] if results['distances'][0] else 0
                    
                    historical_context.append({
                        'topic': topic,
                        'content': doc,
                        'metadata': metadata,
                        'relevance_score': 1 - distance  # Convert distance to similarity
                    })
                    
                    print(f"  Found relevant analysis from {metadata.get('date', 'Unknown date')}")
        
        print(f"\nTotal historical analyses retrieved: {len(historical_context)}")
        return historical_context
    
    def run_news_scout(self):
        """Run enhanced news collection with breaking event detection"""
        print("\n=== PHASE 1: ENHANCED NEWS COLLECTION (Multi-Source) ===")
        
        # Standard search queries
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
        
        # Collect all raw articles from multiple sources
        all_articles = []
        initial_articles = []
        
        for query in search_queries:
            print(f"\nSearching (Tavily + WorldNews): {query}")
            results = multi_source_news_search(query)
            
            # Save raw results for debugging
            debug_dir = Path("debug_outputs")
            debug_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_file = debug_dir / f"raw_news_multi_{timestamp}_{query.replace(' ', '_')[:30]}.json"
            
            with open(debug_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved multi-source results to: {debug_file}")
            
            # Process combined articles with temporal classification
            for article in results['combined_articles']:
                article['query'] = query
                # Add temporal classification
                article['temporal_status'] = self.temporal_parser.classify_event_temporality(
                    article.get('title', ''),
                    article.get('content', '')
                )
                all_articles.append(article)
                initial_articles.append(article)
        
        print(f"\nInitial collection: {len(all_articles)} articles from {len(search_queries)} queries")
        
        # Detect breaking events and generate additional queries
        print("\n=== DETECTING BREAKING EVENTS ===")
        breaking_events, additional_queries = self.event_detector.detect_breaking_events(initial_articles)
        
        if breaking_events:
            print(f"\nDetected {len(breaking_events)} breaking events:")
            for event in breaking_events:
                print(f"  - {event.get('description', 'Unknown event')}")
        
        if additional_queries:
            print(f"\nRunning {len(additional_queries)} additional targeted searches:")
            for query in additional_queries:
                print(f"\nAdaptive search: {query}")
                results = multi_source_news_search(query)
                
                for article in results['combined_articles']:
                    article['query'] = f"BREAKING: {query}"
                    all_articles.append(article)
        
        # Save all articles to markdown file
        self._save_sources_markdown(all_articles, breaking_events)
        
        print(f"\nTotal collected: {len(all_articles)} articles")
        print(f"Sources saved to: {self.sources_filename}")
        
        return all_articles
    
    def _save_sources_markdown(self, articles, breaking_events=None):
        """Save all collected articles to a markdown file with source attribution"""
        os.makedirs('strategy_analyses', exist_ok=True)
        
        with open(self.sources_filename, 'w', encoding='utf-8') as f:
            f.write(f"# GPSE Enhanced News Sources - {self.current_date}\n\n")
            f.write(f"Total Articles Collected: {len(articles)}\n")
            f.write(f"Sources: Tavily AI Search + WorldNewsAPI\n\n")
            
            if breaking_events:
                f.write("## BREAKING EVENTS DETECTED\n\n")
                for event in breaking_events:
                    f.write(f"- {event.get('description', 'Unknown event')}\n")
                f.write("\n---\n\n")
            
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
                    f.write(f"### Article {i} (Source: {article.get('source', 'unknown')})\n")
                    f.write(f"- **Title**: {article['title']}\n")
                    f.write(f"- **URL**: {article['url']}\n")
                    f.write(f"- **Published**: {article['published_date']}\n")
                    if 'author' in article:
                        f.write(f"- **Author**: {article['author']}\n")
                    if 'score' in article:
                        f.write(f"- **Relevance Score**: {article['score']:.3f}\n")
                    f.write(f"- **Content**: {article['content'][:1000]}...\n\n")
                
                f.write("---\n\n")
    
    def run_analyst(self, all_articles, historical_context):
        """Run strategic analysis phase with ALL raw articles and historical context"""
        print("\n=== PHASE 2: STRATEGIC ANALYSIS (Full Context + History) ===")
        
        analyst_prompt = f"""You are a senior strategic analyst providing sophisticated multi-dimensional analysis for {self.current_date}.

TEMPORAL ACCURACY REQUIREMENTS:
- Today is {self.current_date}
- Articles dated today are describing TODAY's events
- If an article says something "happened" or uses past tense, treat it as PAST
- If an article says "after the attack", the attack has ALREADY OCCURRED
- Use correct tense: past events in past tense, ongoing in present, planned in future
- DO NOT describe completed events as future possibilities

You have been provided with:
1. {len(all_articles)} raw news articles from multiple sources (Tavily + WorldNewsAPI)
2. {len(historical_context)} relevant historical analyses from our institutional memory
3. Some articles marked as "BREAKING" indicate urgent developments detected by our system

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

7. LEARNING FROM PAST ASSESSMENTS
   - How do current events relate to our previous analyses?
   - Which past predictions or patterns are being validated/invalidated?
   - What new patterns are emerging compared to historical assessments?
   - Are there recurring themes or cycles we've identified before?

Pay special attention to articles marked as "BREAKING" as they may represent critical developments.
Analyze with maximum specificity. Every claim must reference specific articles.
When referencing historical analyses, cite the date and topic.
Identify patterns across ALL articles, not just within topic areas.
Be explicit about confidence levels and evidence quality."""

        # Format articles for analysis
        articles_text = self._format_articles_for_analysis(all_articles)
        
        # Format historical context
        historical_text = self._format_historical_context(historical_context)
        
        messages = [
            SystemMessage(content=analyst_prompt),
            HumanMessage(content=f"""Analyze these {len(all_articles)} news articles with reference to {len(historical_context)} historical analyses:

CURRENT NEWS ARTICLES:
{articles_text}

RELEVANT HISTORICAL ANALYSES:
{historical_text}

Provide comprehensive strategic analysis that builds on our institutional knowledge.""")
        ]
        
        analysis = self.analyst_llm.invoke(messages)
        print("\nStrategic Analysis Complete")
        
        return analysis.content
    
    def _format_articles_for_analysis(self, articles):
        """Format articles for analyst consumption with source attribution"""
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
                formatted.append(f"[{i}] {article['title']} (Source: {article.get('source', 'unknown')})")
                formatted.append(f"    URL: {article['url']}")
                formatted.append(f"    Date: {article['published_date']}")
                formatted.append(f"    Content: {article['content']}")
                formatted.append("")
        
        return "\n".join(formatted)
    
    def _format_historical_context(self, historical_context):
        """Format historical analyses for analyst reference"""
        if not historical_context:
            return "No relevant historical analyses found."
        
        formatted = []
        
        # Group by topic
        topics = {}
        for item in historical_context:
            topic = item['topic']
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(item)
        
        for topic, items in topics.items():
            formatted.append(f"\n=== HISTORICAL CONTEXT: {topic} ===")
            
            for item in items:
                metadata = item['metadata']
                date = metadata.get('date', 'Unknown date')
                section = metadata.get('section', 'Unknown section')
                relevance = item['relevance_score']
                
                formatted.append(f"\n[{date} - {section}] (Relevance: {relevance:.2f})")
                formatted.append(item['content'][:500] + "...")
                formatted.append("")
        
        return "\n".join(formatted)
    
    def run_communicator(self, analysis, all_articles):
        """Create final intelligence product with access to both analysis and sources"""
        print("\n=== PHASE 3: STRATEGIC COMMUNICATION (Dual Access) ===")
        
        comm_prompt = f"""You are a senior strategic communications specialist creating a professional intelligence assessment for {self.current_date}.

You have access to:
1. The analyst's strategic assessment (which includes historical context)
2. All {len(all_articles)} original news articles from multiple sources (Tavily + WorldNewsAPI)

Your task is to create a comprehensive strategic intelligence assessment that:

TEMPORAL VERIFICATION:
- Verify all events are described in the correct tense
- If sources say "after Israel's attack", describe it as a completed action
- Do not use future tense for events that have already occurred
- Ensure timeline consistency throughout the report

VERIFICATION REQUIREMENTS:
- Fact-check every claim against original sources
- Note source diversity (Tavily vs WorldNewsAPI) for corroboration
- Add missing context the analyst may have overlooked
- Ensure proper source attribution for all claims
- Identify and fill any gaps in the analysis

STRATEGIC DEPTH REQUIREMENTS:
- Explain WHY each development matters strategically
- Show causal chains and interdependencies
- Highlight coalition/alliance dynamics
- Project second and third-order effects

HISTORICAL CONTINUITY REQUIREMENTS:
- Reference relevant past assessments where appropriate
- Show how current events fit into longer-term patterns
- Highlight validated/invalidated predictions from past analyses
- Identify emerging trends compared to historical baseline

BREAKING NEWS EMPHASIS:
- Prioritize any events marked as "BREAKING" in the sources
- Assess immediate implications of breaking developments
- Project likely responses and counter-responses

FORMAT REQUIREMENTS:
1. EXECUTIVE SUMMARY (500 words)
   - Key strategic judgments with confidence levels
   - Most significant developments with strategic WHY
   - Critical decision points and their implications
   - Key insights from historical pattern analysis

2. LEARNING FROM PAST ASSESSMENTS
   - Patterns confirmed by current events
   - Previous predictions validated/invalidated
   - Emerging trends vs historical baseline
   - Institutional knowledge applied to current situation

3. STRATEGIC SITUATION ASSESSMENT
   - Global power dynamics and their drivers
   - Coalition/alliance developments
   - Cross-domain interactions

4. PRIORITY DEVELOPMENTS ANALYSIS
   - Each development with full context
   - Strategic significance explained
   - Cascading effects mapped
   - Historical precedents noted

5. SCENARIO ANALYSIS
   - Multiple futures with drivers
   - Key indicators for each path
   - Decision points that shape outcomes
   - Historical patterns informing scenarios

6. STRATEGIC RECOMMENDATIONS
   - Based on evidence and patterns
   - Account for coalition dynamics
   - Consider second-order effects
   - Informed by institutional memory

7. SOURCE ATTRIBUTION
   - Every claim linked to specific articles
   - Note when multiple sources confirm same information
   - Confidence levels based on source quality and diversity
   - Contradictions explicitly noted
   - Historical references properly cited"""

        # Provide both analysis and article summary
        articles_summary = self._create_articles_summary(all_articles)
        
        messages = [
            SystemMessage(content=comm_prompt),
            HumanMessage(content=f"""Create a strategic intelligence assessment based on:

ANALYST'S ASSESSMENT (includes historical context):
{analysis}

ORIGINAL SOURCES SUMMARY ({len(all_articles)} articles from Tavily + WorldNewsAPI):
{articles_summary}

Ensure every strategic claim can be traced to specific sources and build upon our institutional knowledge.""")
        ]
        
        stream = self.communicator_llm.stream(messages)
        final_report_content = "".join(chunk.content for chunk in stream)
        print("\nFinal Report Complete")
        
        return final_report_content
    
    def _create_articles_summary(self, articles):
        """Create a summary of articles for communicator reference"""
        summary = []
        
        # Group by topic
        topics = {}
        for article in articles:
            query = article['query']
            if query not in topics:
                topics[query] = []
            topics[query].append(f"- [{article.get('source', 'unknown')}] {article['title']} ({article['published_date']}): {article['content'][:200]}...")
        
        for topic, items in topics.items():
            summary.append(f"\n{topic}:")
            summary.extend(items)
        
        return "\n".join(summary)
    
    def store_analysis_in_memory(self, final_report):
        """Store the new analysis in ChromaDB for future reference"""
        print("\n=== STORING ANALYSIS IN MEMORY ===")
        
        try:
            # Generate a unique document ID
            doc_id = f"GGSM-{datetime.now().strftime('%Y%m%d')}-{self.timestamp}"
            
            # Process and store the document
            # First, save it temporarily to process it
            temp_file = f"temp_analysis_{self.timestamp}.md"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(f"""---
## Geopolitical Grand Strategy Monitor
**Strategic Synthesis Entry**
**Date:** {self.current_date}
**Entry ID:** {doc_id}

{final_report}
---""")
            
            # Process the document into chunks and store in ChromaDB
            chunks_added = self.db_manager.process_strategy_document(temp_file)
            
            # Remove temporary file
            os.remove(temp_file)
            
            print(f"Successfully stored {chunks_added} chunks in ChromaDB")
            print(f"Document ID: {doc_id}")
            
        except Exception as e:
            logger.error(f"Error storing analysis in memory: {str(e)}")
    
    def run(self):
        """Execute the enhanced GPSE pipeline with memory"""
        try:
            # Phase 1: Enhanced News Collection with Breaking Event Detection
            all_articles = self.run_news_scout()
            
            # Phase 1.5: Query Historical Context
            # Extract key topics from search queries for historical lookup
            key_topics = [
                "US China Russia strategic competition",
                "Taiwan Ukraine Middle East tensions",
                "cyber warfare AI militarization",
                "economic sanctions trade war",
                "terrorism non-state actors",
                "UN Security Council",
                "critical infrastructure",
                "climate change conflicts"
            ]
            historical_context = self.query_historical_context(key_topics)

            # Prepend the latest weekly landscape report to the historical context
            try:
                # Find the most recent report
                strategy_dir = Path('strategy_analyses')
                report_files = sorted(
                    strategy_dir.glob('Strategic_Landscape_Report-*.md'),
                    key=os.path.getmtime,
                    reverse=True
                )
                if report_files:
                    latest_report_path = report_files[0]
                    with open(latest_report_path, 'r', encoding='utf-8') as f:
                        report_content = f.read()
                    
                    # Add it as a high-priority context item
                    historical_context.insert(0, {
                        'topic': 'Weekly Strategic Landscape',
                        'content': report_content,
                        'metadata': {'date': latest_report_path.stem, 'section': 'Weekly Synthesis'},
                        'relevance_score': 1.0 
                    })
                    print(f"\nSuccessfully loaded and prepended weekly report: {latest_report_path.name}")

            except Exception as e:
                logger.warning(f"Could not load weekly strategic landscape report: {e}")

            # Phase 2: Strategic Analysis (Full Context + History)
            analysis = self.run_analyst(all_articles, historical_context)
            
            # Phase 3: Final Report (Dual Access)
            final_report = self.run_communicator(analysis, all_articles)
            
            # Phase 4: Store in Memory
            doc_id = self.store_analysis_in_memory(final_report)
            
            # Phase 5: Extract and Store Pathways
            if doc_id:
                self.extract_and_store_pathways(final_report, doc_id)

            # Save the report
            os.makedirs('strategy_analyses', exist_ok=True)
            with open(self.output_filename, 'w', encoding='utf-8') as f:
                f.write(final_report)
            
            print(f"\n\nReport saved to: {self.output_filename}")
            print(f"Sources saved to: {self.sources_filename}")
            print(f"Analysis stored in ChromaDB for future reference")
            print(f"Full paths:")
            print(f"  Report: {os.path.abspath(self.output_filename)}")
            print(f"  Sources: {os.path.abspath(self.sources_filename)}")
            
            return final_report
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            raise
    
    def extract_and_store_pathways(self, final_report: str, doc_id: str):
        """Extract strategic pathways from the analysis and store them in ChromaDB"""
        print("\n=== EXTRACTING STRATEGIC PATHWAYS ===")
        
        try:
            # Use the pathway extractor tool to identify pathways
            pathways = pathway_extractor(final_report)
            
            if not pathways:
                print("No strategic pathways identified in this analysis.")
                return
            
            print(f"Identified {len(pathways)} strategic pathways:")
            
            # Store each pathway in the database
            for i, pathway_dict in enumerate(pathways, 1):
                # Update the source_analysis_id to match our document
                pathway_dict['source_analysis_id'] = doc_id
                
                # Generate a unique pathway ID if not provided
                if 'pathway_id' not in pathway_dict:
                    pathway_dict['pathway_id'] = f"pathway_{datetime.now().strftime('%Y%m%d')}_{i:03d}"
                
                # Ensure dates are properly formatted
                pathway_dict['creation_date'] = datetime.now().date().isoformat()
                pathway_dict['last_updated'] = datetime.now().date().isoformat()
                
                # Create the StrategicPathway object
                pathway = StrategicPathway(**pathway_dict)
                
                # Add to database
                self.db_manager.add_pathway(pathway)
                
                print(f"  - {pathway.title} (ID: {pathway.pathway_id})")
                
            print(f"\nSuccessfully stored {len(pathways)} pathways in ChromaDB")
            
        except Exception as e:
            logger.error(f"Error extracting/storing pathways: {str(e)}")
            print(f"Warning: Could not extract pathways - {str(e)}")

def main():
    """Main execution"""
    try:
        print("\n" + "="*70)
        print("GEOPOLITICAL GRAND STRATEGY ENGINE (GPSE)")
        print("ENHANCED VERSION - Multi-Source News + Breaking Event Detection")
        print("="*70 + "\n")
        
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check API keys
        if not os.getenv("OPENAI_API_KEY"):
            print("ERROR: OPENAI_API_KEY not found")
            sys.exit(1)
        
        if not os.getenv("TAVILY_API_KEY"):
            print("ERROR: TAVILY_API_KEY not found")
            sys.exit(1)
        
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("ERROR: ANTHROPIC_API_KEY not found")
            sys.exit(1)
        
        if not os.getenv("WORLDNEWS_API_KEY"):
            print("WARNING: WORLDNEWS_API_KEY not found - will use Tavily only")
        
        # Initialize and run
        gpse = EnhancedGPSEWithMemory()
        result = gpse.run()
        
        print("\n" + "="*50)
        print("ANALYSIS COMPLETE WITH ENHANCED MEMORY")
        print("="*50)
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        logger.exception("Full traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()
