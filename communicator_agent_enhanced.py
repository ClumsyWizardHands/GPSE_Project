"""
Enhanced Communicator Agent Implementation with Multi-File Deep Dive Analysis
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
from pathlib import Path

from crewai import Agent
from crewai.tools import BaseTool
from langchain_openai import ChatOpenAI
import logging

from db_manager import ChromaDBManager
from gpse_tools import get_date_code

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MultiFileWriterTool(BaseTool):
    """
    Enhanced tool for writing both executive briefs and detailed regional deep-dive analyses.
    """
    name: str = "Multi-File Writer Tool"
    description: str = """Write both executive brief and comprehensive deep-dive analyses to separate files.
    Use this tool by providing:
    1. executive_brief: The condensed executive summary
    2. deep_dives: A dictionary with keys for each region/topic and their detailed analyses
    """
    
    def _run(self, executive_brief: str, deep_dives: Dict[str, str] = None, metadata: Dict[str, Any] = None) -> str:
        """
        Write executive brief and multiple deep-dive analysis files.
        
        Args:
            executive_brief: The executive summary content
            deep_dives: Dictionary mapping region/topic names to detailed analysis content
            metadata: Optional metadata to include in file headers
        
        Returns:
            Success message with all file paths created
        """
        try:
            # Ensure strategy_analyses directory exists
            output_dir = Path("strategy_analyses")
            output_dir.mkdir(exist_ok=True)
            
            # Generate date components
            date_code = get_date_code()
            date_str = datetime.now().strftime("%B %d, %Y")
            
            files_created = []
            
            # 1. Write Executive Brief
            exec_filename = f"GGSM-{date_code}-DailyAnalysis.md"
            exec_path = output_dir / exec_filename
            
            # Format executive brief with GPSE structure
            formatted_exec = self._format_executive_brief(executive_brief, date_str, exec_filename)
            
            with open(exec_path, 'w', encoding='utf-8') as f:
                f.write(formatted_exec)
            
            files_created.append(str(exec_path))
            logger.info(f"Executive brief written to: {exec_path}")
            
            # 2. Write Deep Dive Analyses if provided
            if deep_dives:
                for region_topic, analysis_content in deep_dives.items():
                    # Clean the region/topic name for filename
                    clean_name = region_topic.replace(' ', '-').replace('/', '-')
                    dive_filename = f"GGSM-{date_code}-DeepDive-{clean_name}.md"
                    dive_path = output_dir / dive_filename
                    
                    # Format deep dive with enhanced structure
                    formatted_dive = self._format_deep_dive(
                        analysis_content, 
                        region_topic, 
                        date_str, 
                        dive_filename,
                        metadata
                    )
                    
                    with open(dive_path, 'w', encoding='utf-8') as f:
                        f.write(formatted_dive)
                    
                    files_created.append(str(dive_path))
                    logger.info(f"Deep dive analysis written to: {dive_path}")
            
            # 3. Create index file linking all analyses
            index_filename = f"GGSM-{date_code}-Index.md"
            index_path = output_dir / index_filename
            index_content = self._create_index_file(
                date_str, 
                exec_filename, 
                [(region, f"GGSM-{date_code}-DeepDive-{region.replace(' ', '-').replace('/', '-')}.md") 
                 for region in deep_dives.keys()] if deep_dives else []
            )
            
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
            
            files_created.append(str(index_path))
            
            # Save metadata
            if metadata:
                metadata_path = output_dir / f"GGSM-{date_code}-metadata.json"
                metadata['files_created'] = files_created
                metadata['generation_time'] = datetime.now().isoformat()
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
                
                logger.info(f"Metadata saved to: {metadata_path}")
            
            return f"Successfully created {len(files_created)} analysis files:\n" + "\n".join(files_created)
            
        except Exception as e:
            error_msg = f"Failed to write files: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _format_executive_brief(self, content: str, date_str: str, filename: str) -> str:
        """Format the executive brief with standard GPSE structure"""
        entry_id = filename.replace('.md', '')
        
        return f"""---
## Geopolitical Grand Strategy Monitor - Executive Brief
**Strategic Synthesis Entry**
**Date:** {date_str}
**Entry ID:** {entry_id}
**Analysis Type:** Executive Summary
**Classification:** Strategic Intelligence

{content}

### Navigation
- [Full Analysis Index](GGSM-{get_date_code()}-Index.md)
- [Regional Deep Dives Available](#)

---"""

    def _format_deep_dive(self, content: str, region_topic: str, date_str: str, 
                         filename: str, metadata: Dict[str, Any] = None) -> str:
        """Format deep dive analysis with comprehensive structure"""
        entry_id = filename.replace('.md', '')
        
        return f"""---
## Geopolitical Grand Strategy Monitor - Deep Dive Analysis
**Region/Topic:** {region_topic}
**Date:** {date_str}
**Entry ID:** {entry_id}
**Analysis Type:** Comprehensive Regional Assessment
**Classification:** Strategic Intelligence - Detailed

### Analysis Scope
This deep dive provides comprehensive analysis including:
- Complete source verification chains with bias assessments
- Full temporal event sequences with UTC timestamps
- Detailed actor behavior modeling using game theory
- Strategic inference sections with evidence trails
- Counterfactual scenarios and probability assessments
- Cross-regional cascade effects
- Intelligence gaps and collection priorities

---

{content}

### Metadata
**Generated by:** GPSE Enhanced Communicator Agent
**Processing Time:** {datetime.now().strftime("%H:%M:%S UTC")}
**Sources Analyzed:** {metadata.get('sources_count', 'Multiple') if metadata else 'Multiple'}
**Historical Context References:** {metadata.get('historical_refs', 'Integrated') if metadata else 'Integrated'}
**Analytical Depth:** Maximum
**Confidence Levels:** Indicated per assessment

### Related Documents
- [Executive Brief](GGSM-{get_date_code()}-DailyAnalysis.md)
- [Analysis Index](GGSM-{get_date_code()}-Index.md)

---"""

    def _create_index_file(self, date_str: str, exec_filename: str, 
                          deep_dive_files: List[Tuple[str, str]]) -> str:
        """Create an index file linking all analyses"""
        
        deep_dive_links = "\n".join([
            f"- [{region}]({filename})" 
            for region, filename in deep_dive_files
        ])
        
        return f"""---
## Geopolitical Grand Strategy Monitor - Analysis Index
**Date:** {date_str}
**Entry ID:** GGSM-{get_date_code()}-Index

### Available Analyses

#### Executive Brief
- [{exec_filename}]({exec_filename}) - High-level strategic summary for decision makers

#### Regional Deep Dives
{deep_dive_links if deep_dive_links else '- No regional deep dives generated'}

#### Cross-Cutting Analyses
- Global Threats Assessment (if generated)
- Cascade Effect Modeling (if generated)
- Strategic Blind Spots Analysis (if generated)

### Analysis Statistics
- Total Files Generated: {len(deep_dive_files) + 1}
- Processing Date: {date_str}
- Analysis Depth: Comprehensive

### Navigation Guide
1. Start with the Executive Brief for high-level insights
2. Dive into specific regional analyses for detailed assessments
3. Review cross-cutting analyses for systemic perspectives
4. Check metadata files for source attribution and confidence levels

---"""


class EnhancedStrategyDBUpdateTool(BaseTool):
    """
    Enhanced tool for updating ChromaDB with multiple analysis documents at once.
    """
    name: str = "Enhanced Strategy Database Update Tool"
    description: str = "Update the ChromaDB with multiple analysis documents including executive brief and deep dives"
    
    def __init__(self):
        super().__init__()
        self._db_manager = None
    
    @property
    def db_manager(self):
        """Lazy load database manager"""
        if self._db_manager is None:
            self._db_manager = ChromaDBManager()
        return self._db_manager
    
    def _run(self, document_paths: List[str], analysis_type: str = "comprehensive", 
             custom_metadata: Dict[str, Any] = None) -> str:
        """
        Add multiple strategic analysis documents to ChromaDB.
        
        Args:
            document_paths: List of paths to markdown documents to process
            analysis_type: Type of analysis (executive, deep_dive, comprehensive)
            custom_metadata: Optional additional metadata to store
        
        Returns:
            Success message with total chunks added
        """
        try:
            total_chunks = 0
            processed_files = []
            
            for doc_path in document_paths:
                if not os.path.exists(doc_path):
                    logger.warning(f"Document not found: {doc_path}")
                    continue
                
                # Process each document
                logger.info(f"Processing document for ChromaDB: {doc_path}")
                
                # Extract metadata from filename
                filename = os.path.basename(doc_path)
                
                # Determine document subtype
                if "DeepDive" in filename:
                    doc_subtype = "deep_dive"
                elif "Index" in filename:
                    doc_subtype = "index"
                else:
                    doc_subtype = "executive_brief"
                
                base_metadata = {
                    'filename': filename,
                    'processed_date': datetime.now().isoformat(),
                    'document_type': 'strategic_analysis',
                    'analysis_type': analysis_type,
                    'document_subtype': doc_subtype
                }
                
                # Merge with custom metadata
                if custom_metadata:
                    base_metadata.update(custom_metadata)
                
                # Process document
                chunks_added = self.db_manager.process_strategy_document(doc_path)
                total_chunks += chunks_added
                processed_files.append(filename)
                
                logger.info(f"Added {chunks_added} chunks from {filename}")
            
            # Get collection stats
            collection_size = len(self.db_manager.collection.get()['ids'])
            
            success_msg = (
                f"Successfully updated strategy database:\n"
                f"- Documents processed: {len(processed_files)}\n"
                f"- Files: {', '.join(processed_files)}\n"
                f"- Total chunks added: {total_chunks}\n"
                f"- Total documents in database: {collection_size}\n"
                f"- Analysis type: {analysis_type}"
            )
            
            logger.info(success_msg)
            return success_msg
            
        except Exception as e:
            error_msg = f"Failed to update strategy database: {str(e)}"
            logger.error(error_msg)
            return error_msg


def create_enhanced_communicator_agent(llm_instance=None) -> Agent:
    """
    Create the Enhanced Communicator agent with multi-file deep dive capabilities.
    
    Args:
        llm_instance: Optional LLM instance (defaults to GPT-4o-mini)
    
    Returns:
        Configured Enhanced Communicator agent
    """
    # Use provided LLM or create default
    if llm_instance is None:
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            raise ValueError("OpenAI API key required for communicator agent")
        
        llm_instance = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=openai_key
        )
    
    # Create enhanced tools
    multi_writer_tool = MultiFileWriterTool()
    enhanced_db_tool = EnhancedStrategyDBUpdateTool()
    
    # Create enhanced agent with detailed instructions
    communicator = Agent(
        role="Strategic Communications Officer - Deep Analysis Specialist",
        goal=(
            "Transform comprehensive strategic analyses into BOTH:\n"
            "1. A concise executive brief for quick decision-making\n"
            "2. Multiple detailed deep-dive analyses for each region/topic\n"
            "Then save all documents and update the historical knowledge base."
        ),
        backstory=(
            "You are a master of strategic communications with a unique dual capability: "
            "creating both high-level executive summaries AND exhaustively detailed analytical deep dives. "
            "You understand that different audiences need different levels of detail. "
            "Senior decision-makers need crisp, actionable intelligence in the executive brief, "
            "while analysts and regional specialists require the full depth of analysis including:\n\n"
            "- Complete source verification chains with bias assessments\n"
            "- Full temporal event timelines with UTC timestamps\n"
            "- Detailed actor behavior modeling using game theory\n"
            "- Strategic inference sections with comprehensive evidence trails\n"
            "- Counterfactual scenarios with probability assessments\n"
            "- Cross-regional cascade effect modeling\n"
            "- Intelligence gaps and collection priorities\n\n"
            "You excel at extracting every analytical insight from the geo_analyst's work "
            "and presenting it in structured, actionable formats. Your deep dives leave no "
            "stone unturned, providing the full analytical depth that the GPSE system generates."
        ),
        tools=[multi_writer_tool, enhanced_db_tool],
        llm=llm_instance,
        max_iter=5,
        allow_delegation=False,
        verbose=True
    )
    
    return communicator


# Test function for the enhanced communicator
def test_enhanced_communicator():
    """Test the enhanced communicator with sample multi-region content"""
    logger.info("Testing Enhanced Communicator Agent...")
    
    # Sample executive brief
    exec_brief = """
### Executive Summary
Global geopolitical tensions have reached critical thresholds across multiple regions, 
with particular concern in the Indo-Pacific, Eastern Europe, and Middle East. 
Coordinated responses from major powers suggest a shift toward strategic competition 
rather than cooperation.

### Key Findings
1. Indo-Pacific: Naval escalation near Taiwan Strait
2. Eastern Europe: NATO expansion tensions with Russia
3. Middle East: Iran-Israel proxy conflicts intensifying
4. Africa: Resource competition between China and Western powers
5. Latin America: Democratic backsliding and external influence

### Strategic Recommendations
- Immediate: Enhance intelligence collection in Taiwan Strait
- Short-term: Strengthen NATO eastern flank deterrence
- Long-term: Develop comprehensive Indo-Pacific strategy
"""

    # Sample deep dives
    deep_dives = {
        "Indo-Pacific": """
## Comprehensive Indo-Pacific Analysis

### Source Verification Chain
**Primary Sources:**
- Reuters (Center bias, Very High factual, Western perspective) - 14:32 UTC June 8, 2025
  - "Chinese naval forces conduct live-fire exercises 100km from Taiwan"
  - Source: Embedded Reuters correspondent with Japanese Maritime Self-Defense Force
  - Verification: Satellite imagery from Maxar Technologies confirms vessel positions

- Xinhua (Left bias, Mixed factual, Chinese state perspective) - 15:45 UTC June 8, 2025  
  - "PLA Navy conducts routine training in Chinese territorial waters"
  - Source: PLA Navy spokesperson Sr. Col. Zhang Wei
  - Contradiction noted: Claims "routine" despite largest deployment since 2022

**Temporal Event Sequence:**
- 06:00 UTC: US Navy P-8 Poseidon detected unusual PLAN submarine activity
- 08:30 UTC: Taiwan Defense Ministry raises alert level
- 10:00 UTC: First PLAN destroyers enter exercise area
- 14:00 UTC: Live fire exercises commence
- 16:00 UTC: Japanese vessels shadow Chinese formation
- 18:00 UTC: US carrier strike group alters course toward region

### Actor Behavior Analysis (Game Theory Model)

**China's Strategic Calculus:**
- Objective Function: Maximize pressure on Taiwan while avoiding US military response
- Constraints: Economic dependencies, domestic stability requirements
- Payoff Matrix:
  - Continue escalation: +8 domestic prestige, -6 economic risk
  - Maintain status quo: +2 stability, -4 nationalist pressure
  - De-escalate: -5 domestic credibility, +3 international relations

**US Response Framework:**
- Primary Goal: Maintain strategic ambiguity while ensuring deterrence
- Tools Available: Naval presence, economic sanctions, diplomatic pressure
- Decision Tree Analysis shows 65% probability of freedom of navigation operation within 72 hours

### Strategic Inferences
**STRATEGIC INFERENCE:** The timing of Chinese exercises coincides with:
1. US Congressional delegation visiting Taipei (arriving 06:00 UTC June 9)
2. Japanese-Australian joint naval exercises 500km to the east
3. Unusual silence from North Korea (typically coordinates provocations)

This suggests a calculated probe of allied resolve rather than preparation for immediate action.

### Counterfactual Scenarios
**Scenario 1: Escalation Pathway (25% probability)**
- Trigger: Accidental collision or fire control radar lock
- Chinese Response: Claim self-defense, mobilize nationalism
- US Response: Deploy additional carrier strike groups
- Escalation ladder: Economic sanctions → Cyber attacks → Limited kinetic action
- Key Indicator: Watch for Chinese civilian maritime militia deployments

**Scenario 2: Diplomatic Off-Ramp (60% probability)**
- Face-saving mechanism: "Conclude successful training"
- Back-channel negotiations through Singapore
- Key Indicator: Reduced Chinese media coverage within 48 hours

### Intelligence Gaps
- CRITICAL: No visibility on PLAN submarine positions
- HIGH: Chinese leadership decision-making process opaque
- MEDIUM: Taiwan's true military readiness status
- COLLECTION PRIORITY: Increase SIGINT coverage of PLA Eastern Theater Command
""",

        "Eastern Europe": """
## Comprehensive Eastern Europe Analysis

### Source Verification Chain
**Primary Sources:**
- BBC News (Center-left bias, High factual, UK perspective) - 09:15 UTC June 8, 2025
  - "NATO announces permanent brigade deployments to Baltic states"
  - Source: NATO Secretary General press conference
  - Verification: Official NATO transcript DOCC-2025-0608-001

[Content continues with similar detail...]

### Temporal Anomaly Analysis
**ANOMALY DETECTED:** Russian strategic bomber deployments to Kaliningrad occurred 
36 hours before NATO announcement, suggesting intelligence leak or preemptive positioning.

- Pattern Break: Typical Russian response time is 12-24 hours post-NATO announcement
- Friction Indicator: Narrative Friction - Russian MOD claims "scheduled rotation" 
  contradicts unusual Tu-160 bomber presence
"""
    }

    try:
        # Create enhanced communicator
        multi_writer = MultiFileWriterTool()
        
        # Test multi-file writing
        result = multi_writer._run(
            executive_brief=exec_brief,
            deep_dives=deep_dives,
            metadata={
                'sources_count': 47,
                'historical_refs': 23,
                'analysis_depth': 'maximum',
                'confidence_high': 15,
                'confidence_medium': 8,
                'confidence_low': 3
            }
        )
        
        logger.info(f"Multi-file write result: {result}")
        logger.info("Enhanced Communicator test completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    # Run test
    test_enhanced_communicator()
