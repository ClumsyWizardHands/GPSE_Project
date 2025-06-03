"""
Enhanced GPSE Tools Module with Multiple News API Support
Uses Tavily and World News API as primary sources with NewsAPI as fallback
Fixed version that properly handles tool calls within tools
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# CrewAI imports
from crewai.tools import tool
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _internal_news_search(query: str) -> List[Dict[str, Any]]:
    """
    Internal news search function that returns raw results.
    This is used by both the enhanced_news_search tool and the aggregator.
    """
    results = []
    
    # Try Tavily (Primary Source 1)
    tavily_key = os.environ.get('TAVILY_API_KEY')
    if tavily_key:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=tavily_key)
            
            # Search parameters
            search_params = {
                "query": query,
                "max_results": 8,
                "search_depth": "advanced",
                "topic": "news",
                "days": 2  # Last 48 hours
            }
            
            logger.info(f"Searching Tavily for: {query}")
            tavily_results = client.search(**search_params)
            
            if tavily_results and 'results' in tavily_results:
                for item in tavily_results['results']:
                    results.append({
                        'source': 'Tavily',
                        'title': item.get('title', 'No title'),
                        'url': item.get('url', ''),
                        'content': item.get('content', '')[:500],
                        'published_date': item.get('published_date', ''),
                        'relevance_score': item.get('score', 0.0)
                    })
                logger.info(f"Found {len(results)} results from Tavily")
        except Exception as e:
            logger.warning(f"Tavily search failed: {e}")
    
    # Try World News API (Primary Source 2)
    world_news_key = os.environ.get('WORLD_NEWS_API_KEY')
    if world_news_key and world_news_key != 'your_world_news_api_key_here':
        try:
            # Calculate date range
            to_date = datetime.now().strftime('%Y-%m-%d')
            from_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
            
            # World News API endpoint
            url = "https://api.worldnewsapi.com/search-news"
            params = {
                'api-key': world_news_key,
                'text': query,
                'language': 'en',
                'earliest-publish-date': from_date,
                'latest-publish-date': to_date,
                'sort': 'relevance',
                'sort-direction': 'desc',
                'number': 8
            }
            
            logger.info(f"Searching World News API for: {query}")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'news' in data:
                    for article in data['news']:
                        results.append({
                            'source': 'World News API',
                            'title': article.get('title', 'No title'),
                            'url': article.get('url', ''),
                            'content': article.get('text', '')[:500],
                            'published_date': article.get('publish_date', ''),
                            'relevance_score': 0.85  # World News API uses different scoring
                        })
                    logger.info(f"Added {len(data['news'])} results from World News API")
        except Exception as e:
            logger.warning(f"World News API search failed: {e}")
    
    # Try NewsAPI.org as additional fallback
    news_api_key = os.environ.get('NEWS_API_KEY')
    if news_api_key and news_api_key != 'your_news_api_key_here' and len(results) < 10:
        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=2)
            
            # NewsAPI endpoint
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'apiKey': news_api_key,
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d'),
                'sortBy': 'relevancy',
                'language': 'en',
                'pageSize': 10 - len(results)  # Only get what we need
            }
            
            logger.info(f"Searching NewsAPI for: {query}")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok' and data.get('articles'):
                    for article in data['articles']:
                        results.append({
                            'source': 'NewsAPI',
                            'title': article.get('title', 'No title'),
                            'url': article.get('url', ''),
                            'content': article.get('description', '')[:500],
                            'published_date': article.get('publishedAt', ''),
                            'relevance_score': 0.8  # NewsAPI doesn't provide scores
                        })
                    logger.info(f"Added {len(data['articles'])} results from NewsAPI")
        except Exception as e:
            logger.warning(f"NewsAPI search failed: {e}")
    
    return results


@tool("Enhanced News Search")
def enhanced_news_search(query: str) -> str:
    """
    Enhanced news search that uses multiple APIs simultaneously:
    1. Tavily API (primary source)
    2. World News API (primary source)
    3. NewsAPI.org (additional fallback)
    
    This ensures comprehensive news coverage from multiple sources.
    You MUST use this tool to search for news - do not provide hypothetical results.
    """
    results = _internal_news_search(query)
    
    # Format and return results
    if not results:
        return f"No news articles found for query: {query}. Please ensure API keys are configured correctly in the .env file."
    
    # Sort by relevance score and remove duplicates
    seen_urls = set()
    unique_results = []
    for item in sorted(results, key=lambda x: x['relevance_score'], reverse=True):
        if item['url'] not in seen_urls:
            seen_urls.add(item['url'])
            unique_results.append(item)
    
    # Format results
    formatted_results = [f"Found {len(unique_results)} unique news articles for '{query}' from {len(set(r['source'] for r in unique_results))} sources:\n"]
    
    for i, item in enumerate(unique_results[:20], 1):  # Limit to 20 results
        formatted_results.append(f"\n--- Article {i} ---")
        formatted_results.append(f"Title: {item['title']}")
        formatted_results.append(f"URL: {item['url']}")
        formatted_results.append(f"Source: {item['source']}")
        if item['published_date']:
            formatted_results.append(f"Published: {item['published_date']}")
        formatted_results.append(f"Summary: {item['content']}")
        if item['relevance_score'] > 0:
            formatted_results.append(f"Relevance: {item['relevance_score']:.2f}")
    
    return "\n".join(formatted_results)


@tool("Direct URL News Fetch")
def fetch_news_from_url(url: str) -> str:
    """
    Directly fetch and extract content from a news article URL.
    Use this when you have specific URLs to analyze in detail.
    This tool MUST be used to get full article content - do not make up content.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        logger.info(f"Fetching article from: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return f"Failed to fetch article. HTTP status: {response.status_code}"
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Extract article content
        article_content = []
        
        # Get title
        title = soup.find('title')
        if title:
            article_content.append(f"Title: {title.get_text(strip=True)}")
        
        # Try to find article body
        article_selectors = [
            'article',
            '[class*="article-body"]',
            '[class*="story-body"]',
            '[class*="content-body"]',
            'main'
        ]
        
        article_body = None
        for selector in article_selectors:
            article_body = soup.select_one(selector)
            if article_body:
                break
        
        if article_body:
            # Get paragraphs
            paragraphs = article_body.find_all('p')
            content_text = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 30:
                    content_text.append(text)
            
            if content_text:
                article_content.append("\nContent:")
                article_content.extend(content_text[:20])  # Limit paragraphs
        
        if len(article_content) > 1:
            return "\n\n".join(article_content)
        else:
            return f"Could not extract meaningful content from {url}"
            
    except Exception as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return f"Error fetching article: {str(e)}"


@tool("Geopolitical News Aggregator")
def aggregate_geopolitical_news(focus_areas: List[str]) -> str:
    """
    Aggregate news from multiple sources for specific geopolitical focus areas.
    Uses both Tavily and World News API as primary sources for comprehensive coverage.
    Provide a list of focus areas like ['Ukraine conflict', 'China-Taiwan', 'Middle East'].
    This tool MUST be used to gather comprehensive news - do not provide hypothetical results.
    """
    all_results = []
    
    # Default focus areas if none provided
    if not focus_areas:
        focus_areas = [
            "Ukraine Russia conflict latest developments",
            "Middle East tensions Israel Gaza Iran",
            "China Taiwan relations military",
            "cyber warfare attacks ransomware",
            "NATO military developments weapons"
        ]
    
    logger.info(f"Aggregating news for focus areas: {focus_areas}")
    
    # Search for each focus area using the internal function
    for area in focus_areas[:5]:  # Limit to 5 areas
        logger.info(f"Searching for: {area}")
        
        # Use the internal news search function
        results = _internal_news_search(area)
        
        if results:
            # Format results for this focus area
            area_results = [f"\n{'='*60}"]
            area_results.append(f"FOCUS AREA: {area}")
            area_results.append(f"{'='*60}")
            
            # Sort by relevance and format
            seen_urls = set()
            unique_results = []
            for item in sorted(results, key=lambda x: x['relevance_score'], reverse=True):
                if item['url'] not in seen_urls:
                    seen_urls.add(item['url'])
                    unique_results.append(item)
            
            area_results.append(f"Found {len(unique_results)} articles from {len(set(r['source'] for r in unique_results))} sources:\n")
            
            for i, item in enumerate(unique_results[:10], 1):  # Limit to 10 per area
                area_results.append(f"\n--- Article {i} ---")
                area_results.append(f"Title: {item['title']}")
                area_results.append(f"URL: {item['url']}")
                area_results.append(f"Source: {item['source']}")
                if item['published_date']:
                    area_results.append(f"Published: {item['published_date']}")
                area_results.append(f"Summary: {item['content']}")
                if item['relevance_score'] > 0:
                    area_results.append(f"Relevance: {item['relevance_score']:.2f}")
            
            all_results.extend(area_results)
    
    if all_results:
        # Add source summary at the beginning
        sources_used = []
        if os.environ.get('TAVILY_API_KEY'):
            sources_used.append("Tavily")
        if os.environ.get('WORLD_NEWS_API_KEY') and os.environ.get('WORLD_NEWS_API_KEY') != 'your_world_news_api_key_here':
            sources_used.append("World News API")
        if os.environ.get('NEWS_API_KEY') and os.environ.get('NEWS_API_KEY') != 'your_news_api_key_here':
            sources_used.append("NewsAPI")
        
        summary = f"Aggregated geopolitical news for {len(focus_areas)} focus areas\n"
        summary += f"Active news sources: {', '.join(sources_used)}\n"
        summary += "\n".join(all_results)
        return summary
    else:
        return "Unable to aggregate news. Please check API configurations."


# Export tool instances for use in agents
news_search_tool = enhanced_news_search
url_fetch_tool = fetch_news_from_url
news_aggregator_tool = aggregate_geopolitical_news


if __name__ == "__main__":
    # Test the enhanced tools
    print("Testing Enhanced News Tools...")
    print(f"Configured APIs:")
    print(f"- Tavily: {'✓' if os.environ.get('TAVILY_API_KEY') else '✗'}")
    print(f"- World News API: {'✓' if os.environ.get('WORLD_NEWS_API_KEY') and os.environ.get('WORLD_NEWS_API_KEY') != 'your_world_news_api_key_here' else '✗'}")
    print(f"- NewsAPI: {'✓' if os.environ.get('NEWS_API_KEY') and os.environ.get('NEWS_API_KEY') != 'your_news_api_key_here' else '✗'}")
    
    # Test search using the raw function
    print("\nTesting internal search function...")
    results = _internal_news_search("Ukraine Russia conflict latest")
    print(f"Found {len(results)} results")
    
    # Test the tools
    print("\nTesting Enhanced News Search tool...")
    result_str = enhanced_news_search.run("Ukraine conflict")
    print(f"Search Result:\n{result_str[:500]}...")
    
    # Test aggregator
    print("\nTesting Geopolitical News Aggregator tool...")
    focus_areas = ["Ukraine conflict", "Middle East tensions"]
    aggregated = aggregate_geopolitical_news.run(focus_areas)
    print(f"Aggregated Result:\n{aggregated[:500]}...")
