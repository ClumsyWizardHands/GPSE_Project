"""
Enhanced Save Analysis Tool for GPSE Communicator
Combines outputs from both News Scout and Geo Analyst into comprehensive reports
"""
import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Union, List, Tuple
from crewai.tools import BaseTool
from pydantic import Field
import logging

logger = logging.getLogger(__name__)

class ExtractComprehensiveAnalysisTool(BaseTool):
    """
    Tool to extract and combine outputs from both News Scout and Geo Analyst.
    Creates a comprehensive report with strategic analysis and news appendix.
    """
    name: str = "Extract Comprehensive Analysis"
    description: str = """Extract and combine outputs from both News Scout and Geo Analyst agents.
    This tool identifies which content comes from which agent and structures them appropriately.
    Pass the complete context as a single string parameter called 'context_data'."""
    
    def _run(self, context_data: Union[str, Dict]) -> Dict[str, Any]:
        """
        Extract both news data and strategic analysis from the context.
        
        Args:
            context_data: The raw context containing outputs from both agents
        
        Returns:
            Dictionary with separated news and analysis content
        """
        try:
            # Convert to string if needed
            if isinstance(context_data, dict):
                context_str = json.dumps(context_data, indent=2)
            else:
                context_str = str(context_data)
            
            # Split content into sections
            lines = context_str.split('\n')
            
            # Identify News Scout content (typically contains URLs, sources, JSON-like structure)
            news_content = []
            analysis_content = []
            current_section = None
            
            # Markers for News Scout content
            news_markers = [
                '"url":', '"source":', '"title":', '"date":', '"summary":',
                'news.google.com', 'reuters.com', 'bbc.com', 'cnn.com',
                'News Scout', 'Information Curation', 'news articles'
            ]
            
            # Markers for Geo Analyst content
            analysis_markers = [
                'Executive Summary', 'Primary Observations', 'Strategic Analysis',
                'Key Actors', 'Scenario Implications', 'Inferred Strategic',
                'Observable Behavior', 'Strategic Implications', 'Scenario Analysis',
                'Geopolitical', 'strategic shift', 'implications'
            ]
            
            # Process lines to identify sections
            for i, line in enumerate(lines):
                # Check if this is news content
                if any(marker in line for marker in news_markers):
                    current_section = 'news'
                # Check if this is analysis content
                elif any(marker in line for marker in analysis_markers):
                    current_section = 'analysis'
                
                # Add to appropriate section
                if current_section == 'news':
                    news_content.append(line)
                elif current_section == 'analysis':
                    analysis_content.append(line)
            
            # Join content sections
            news_text = '\n'.join(news_content)
            analysis_text = '\n'.join(analysis_content)
            
            # If we didn't find clear sections, try alternative approach
            if not analysis_text:
                # Look for content after "Geo Analyst" or similar markers
                for i, line in enumerate(lines):
                    if 'Geo Analyst' in line or 'Strategic Analysis' in line:
                        analysis_text = '\n'.join(lines[i:])
                        break
            
            # Extract structured news data
            news_items = self._extract_news_items(news_text)
            
            # Extract metadata from both sections
            metadata = self._extract_metadata(context_str, news_items)
            
            result = {
                'analysis_content': analysis_text if analysis_text else self._extract_fallback_analysis(context_str),
                'news_content': news_text,
                'news_items': news_items,
                'metadata': metadata
            }
            
            logger.info(f"Extracted comprehensive analysis with {len(news_items)} news items")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting comprehensive analysis: {str(e)}")
            return {
                'analysis_content': str(context_data),
                'news_content': '',
                'news_items': [],
                'metadata': {
                    'actors': [],
                    'themes': [],
                    'sources_count': 0,
                    'confidence': 'Low'
                }
            }
    
    def _extract_news_items(self, news_text: str) -> List[Dict[str, Any]]:
        """Extract structured news items from news content"""
        news_items = []
        
        try:
            # Try to parse JSON blocks
            json_pattern = r'\{[^{}]*\}'
            json_matches = re.finditer(json_pattern, news_text, re.DOTALL)
            
            for match in json_matches:
                try:
                    item = json.loads(match.group())
                    if 'title' in item or 'url' in item:
                        news_items.append(item)
                except:
                    pass
            
            # If no JSON found, try to extract from structured text
            if not news_items:
                # Look for patterns like "Title: ... URL: ... Date: ..."
                item_pattern = r'(?:Title|Article|Story):\s*([^\n]+).*?(?:URL|Link):\s*([^\n]+).*?(?:Date|Published):\s*([^\n]+)'
                matches = re.finditer(item_pattern, news_text, re.DOTALL | re.IGNORECASE)
                
                for match in matches:
                    news_items.append({
                        'title': match.group(1).strip(),
                        'url': match.group(2).strip(),
                        'date': match.group(3).strip()
                    })
        
        except Exception as e:
            logger.error(f"Error extracting news items: {str(e)}")
        
        return news_items
    
    def _extract_fallback_analysis(self, context_str: str) -> str:
        """Fallback method to extract analysis content"""
        # Look for the longest continuous section that looks like analysis
        sections = context_str.split('\n\n')
        analysis_sections = []
        
        for section in sections:
            if len(section) > 200 and any(marker in section for marker in 
                ['analysis', 'strategic', 'implications', 'scenario', 'observations']):
                analysis_sections.append(section)
        
        return '\n\n'.join(analysis_sections) if analysis_sections else context_str
    
    def _extract_metadata(self, context_str: str, news_items: List[Dict]) -> Dict[str, Any]:
        """Extract metadata from the full context"""
        actors = set()
        themes = set()
        
        # Extract actors (countries, organizations)
        actor_pattern = r'\b(United States|US|USA|China|Russia|NATO|EU|European Union|Ukraine|Israel|Iran|India|Japan|North Korea|South Korea)\b'
        actor_matches = re.findall(actor_pattern, context_str, re.IGNORECASE)
        actors.update(match.upper() for match in actor_matches)
        
        # Extract themes from section headers
        header_pattern = r'^#{1,4}\s*(.+)$'
        header_matches = re.findall(header_pattern, context_str, re.MULTILINE)
        themes.update(match.strip() for match in header_matches if len(match.strip()) < 50)
        
        return {
            'actors': list(actors)[:15],
            'themes': list(themes)[:10],
            'sources_count': len(news_items),
            'news_sources': list(set(item.get('source', '') for item in news_items if item.get('source')))[:10],
            'confidence': 'High' if len(actors) > 3 and len(news_items) > 5 else 'Medium'
        }


class SaveComprehensiveAnalysisTool(BaseTool):
    """
    Tool to save a comprehensive analysis document that combines strategic analysis with news appendix.
    """
    name: str = "Save Comprehensive Analysis"
    description: str = """Save a comprehensive strategic analysis document that includes both the main strategic 
    analysis from the Geo Analyst and a news intelligence appendix from the News Scout.
    This creates a complete intelligence product with both analysis and source data."""
    
    def _run(self, 
             analysis_content: str, 
             news_items: List[Dict[str, Any]] = None,
             metadata: Dict[str, Any] = None) -> str:
        """
        Save the comprehensive analysis document.
        
        Args:
            analysis_content: The main strategic analysis from Geo Analyst
            news_items: List of news items from News Scout
            metadata: Optional metadata about the analysis
        
        Returns:
            Success message with file path
        """
        try:
            # Ensure strategy_analyses directory exists
            output_dir = Path("strategy_analyses")
            output_dir.mkdir(exist_ok=True)
            
            # Generate filename with current date
            date_str = datetime.now().strftime("%B %d, %Y")
            date_code = datetime.now().strftime("%B %d, %Y")
            filename = f"GGSM-{date_code}-DailyAnalysis.md"
            
            # Full file path
            file_path = output_dir / filename
            
            # Build the comprehensive document
            document_parts = []
            
            # Add header
            header = f"""---
## Geopolitical Grand Strategy Monitor
**Strategic Synthesis Entry**
**Date:** {date_str}
**Entry ID:** GGSM-{date_code}
**Analysis Type:** Comprehensive Daily Assessment with Intelligence Sources
**Classification:** Strategic Intelligence
---

"""
            document_parts.append(header)
            
            # Add main strategic analysis
            if not analysis_content.startswith("## Executive Summary") and "Executive Summary" not in analysis_content[:200]:
                document_parts.append("## Strategic Analysis\n\n")
            
            document_parts.append(analysis_content)
            
            # Add news intelligence appendix if available
            if news_items and len(news_items) > 0:
                appendix = self._create_news_appendix(news_items, metadata)
                document_parts.append(appendix)
            
            # Add footer with metadata
            if metadata:
                footer = f"""

---
### Analysis Metadata
**Processing Time:** {datetime.now().strftime("%H:%M:%S EST")}
**Total Sources Analyzed:** {metadata.get('sources_count', 'Multiple')}
**Key Actors Identified:** {', '.join(metadata.get('actors', [])[:10])}
**Strategic Themes:** {', '.join(metadata.get('themes', [])[:5])}
**News Sources:** {', '.join(metadata.get('news_sources', [])[:5])}
**Confidence Level:** {metadata.get('confidence', 'High')}
---"""
                document_parts.append(footer)
            
            # Combine all parts
            full_document = ''.join(document_parts)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(full_document)
            
            logger.info(f"Successfully saved comprehensive analysis to: {file_path}")
            
            return f"Successfully saved comprehensive strategic analysis to {file_path.absolute()}"
            
        except Exception as e:
            error_msg = f"Failed to save comprehensive analysis: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _create_news_appendix(self, news_items: List[Dict[str, Any]], metadata: Dict[str, Any]) -> str:
        """Create a formatted news intelligence appendix"""
        appendix_parts = ["\n\n---\n\n## Appendix: News Intelligence Sources\n\n"]
        
        appendix_parts.append("### Intelligence Summary\n\n")
        appendix_parts.append(f"This analysis was informed by {len(news_items)} news sources ")
        appendix_parts.append(f"covering key geopolitical developments.\n\n")
        
        # Group news by region/topic if possible
        categorized_news = self._categorize_news(news_items)
        
        for category, items in categorized_news.items():
            appendix_parts.append(f"### {category}\n\n")
            
            for item in items[:10]:  # Limit to 10 items per category
                title = item.get('title', 'Untitled')
                url = item.get('url', '')
                date = item.get('date', 'Date unknown')
                source = item.get('source', 'Unknown source')
                summary = item.get('summary', '')
                
                appendix_parts.append(f"**{title}**\n")
                appendix_parts.append(f"- Source: {source}\n")
                appendix_parts.append(f"- Date: {date}\n")
                if url:
                    appendix_parts.append(f"- Link: {url}\n")
                if summary:
                    appendix_parts.append(f"- Summary: {summary}\n")
                appendix_parts.append("\n")
        
        return ''.join(appendix_parts)
    
    def _categorize_news(self, news_items: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Categorize news items by region or topic"""
        categories = {
            'Russia & Eastern Europe': [],
            'China & Asia-Pacific': [],
            'Middle East': [],
            'United States & Americas': [],
            'Europe & NATO': [],
            'Global & Other': []
        }
        
        # Keywords for categorization
        category_keywords = {
            'Russia & Eastern Europe': ['russia', 'ukraine', 'putin', 'moscow', 'kremlin', 'belarus', 'eastern europe'],
            'China & Asia-Pacific': ['china', 'beijing', 'xi jinping', 'taiwan', 'south china sea', 'asia', 'japan', 'korea'],
            'Middle East': ['middle east', 'israel', 'iran', 'syria', 'saudi', 'gaza', 'lebanon', 'iraq'],
            'United States & Americas': ['united states', 'us ', 'usa', 'america', 'washington', 'biden', 'pentagon'],
            'Europe & NATO': ['europe', 'eu ', 'nato', 'france', 'germany', 'uk ', 'britain', 'brussels']
        }
        
        for item in news_items:
            text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
            categorized = False
            
            for category, keywords in category_keywords.items():
                if any(keyword in text for keyword in keywords):
                    categories[category].append(item)
                    categorized = True
                    break
            
            if not categorized:
                categories['Global & Other'].append(item)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}


# Export tools
extract_comprehensive_analysis = ExtractComprehensiveAnalysisTool()
save_comprehensive_analysis = SaveComprehensiveAnalysisTool()
