"""
Custom Save Analysis Tool for GPSE Communicator
Ensures the actual strategic analysis is saved, not just a QA report
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Union
from crewai.tools import BaseTool
from pydantic import Field
import logging

logger = logging.getLogger(__name__)

class SaveStrategicAnalysisTool(BaseTool):
    """
    Tool specifically designed to save the complete strategic analysis from the Geo Analyst.
    This tool ensures the actual analysis content is saved, not just a quality report.
    """
    name: str = "Save Strategic Analysis"
    description: str = """Save the complete strategic analysis document to the strategy_analyses directory.
    CRITICAL: You must save the ENTIRE strategic analysis from the Geo Analyst, not a quality report about it.
    The saved document should contain all the geopolitical insights, actor analyses, and strategic implications."""
    
    def _run(self, analysis_content: str, metadata: Dict[str, Any] = None) -> str:
        """
        Save the strategic analysis content to a file.
        
        Args:
            analysis_content: The COMPLETE strategic analysis from the Geo Analyst
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
            date_code = datetime.now().strftime("%B %d, %Y")  # Full date format
            filename = f"GGSM-{date_code}-DailyAnalysis.md"
            
            # Full file path
            file_path = output_dir / filename
            
            # Add GPSE header if not present
            if not analysis_content.startswith("---"):
                header = f"""---
## Geopolitical Grand Strategy Monitor
**Strategic Synthesis Entry**
**Date:** {date_str}
**Entry ID:** GGSM-{date_code}
**Analysis Type:** Comprehensive Daily Assessment
**Classification:** Strategic Intelligence
---

"""
                analysis_content = header + analysis_content
            
            # Add footer with quality metadata if provided
            if metadata:
                footer = f"""

---
### Quality Assurance Metadata
**Processing Time:** {datetime.now().strftime("%H:%M:%S EST")}
**Sources Analyzed:** {metadata.get('sources_count', 'Multiple')}
**Key Actors Identified:** {', '.join(metadata.get('actors', []))}
**Strategic Themes:** {', '.join(metadata.get('themes', []))}
**Confidence Level:** {metadata.get('confidence', 'High')}
---"""
                analysis_content += footer
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(analysis_content)
            
            logger.info(f"Successfully saved strategic analysis to: {file_path}")
            
            # No debug output - save directly to the main file only
            
            return f"Successfully saved complete strategic analysis to {file_path.absolute()}"
            
        except Exception as e:
            error_msg = f"Failed to save strategic analysis: {str(e)}"
            logger.error(error_msg)
            return error_msg


class ExtractAnalysisContentTool(BaseTool):
    """
    Tool to help the Communicator extract the actual analysis content from the context.
    This ensures we're working with the real analysis, not generating a new one.
    """
    name: str = "Extract Analysis Content"
    description: str = """Extract and format the complete strategic analysis from the previous agents' outputs.
    This tool helps you identify and extract the ACTUAL analysis content, not create a quality report about it.
    Pass the complete context as a single string parameter called 'context_data'."""
    
    def _run(self, context_data: Union[str, Dict]) -> Dict[str, Any]:
        """
        Extract the strategic analysis content from the context.
        
        Args:
            context_data: The raw context containing the analysis (string or dict)
        
        Returns:
            Dictionary with extracted analysis and metadata
        """
        try:
            # Handle both string and dict inputs
            if isinstance(context_data, dict):
                # If it's a dict, try to extract the actual content
                if 'description' in context_data:
                    context_str = str(context_data['description'])
                elif 'content' in context_data:
                    context_str = str(context_data['content'])
                else:
                    # Convert the entire dict to string
                    context_str = json.dumps(context_data, indent=2)
            else:
                context_str = str(context_data)
            
            # Look for key sections that indicate the actual analysis
            analysis_markers = [
                "Executive Summary",
                "Primary Observations",
                "Strategic Analysis",
                "Key Actors",
                "Scenario Implications",
                "Inferred Strategic",
                "Observable Behavior",
                "Strategic Implications",
                "Scenario Analysis"
            ]
            
            # Extract content between analysis markers
            extracted_content = []
            lines = context_str.split('\n')
            capturing = False
            
            for line in lines:
                # Start capturing when we find analysis markers
                if any(marker in line for marker in analysis_markers):
                    capturing = True
                
                if capturing:
                    extracted_content.append(line)
            
            # Join the extracted content
            analysis = '\n'.join(extracted_content) if extracted_content else context_str
            
            # Extract metadata
            actors = []
            themes = []
            
            # Simple extraction of actors (countries/entities in capitals or with colons)
            for line in lines:
                if ':' in line and any(word.isupper() for word in line.split()):
                    potential_actor = line.split(':')[0].strip().strip('*').strip('#').strip()
                    if len(potential_actor) < 30 and potential_actor:  # Reasonable length for actor name
                        actors.append(potential_actor)
            
            # Extract themes from headers
            for line in lines:
                if line.startswith('###') or line.startswith('####'):
                    theme = line.strip('#').strip()
                    if theme and len(theme) < 50:
                        themes.append(theme)
            
            result = {
                'analysis_content': analysis,
                'metadata': {
                    'actors': list(set(actors))[:10],  # Unique actors, max 10
                    'themes': list(set(themes))[:5],   # Unique themes, max 5
                    'sources_count': context_str.count('http'),  # Count URLs as sources
                    'confidence': 'High' if len(analysis) > 1000 else 'Medium'
                }
            }
            
            logger.info(f"Extracted analysis with {len(actors)} actors and {len(themes)} themes")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting analysis: {str(e)}")
            # Return the original content as fallback
            return {
                'analysis_content': str(context_data),
                'metadata': {
                    'actors': [],
                    'themes': [],
                    'sources_count': 0,
                    'confidence': 'Low'
                }
            }


# Export tools
save_strategic_analysis = SaveStrategicAnalysisTool()
extract_analysis_content = ExtractAnalysisContentTool()
