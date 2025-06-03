"""
Conditional Tasks for GPSE - Quality Control and Retry Logic
"""
from typing import Dict, Any
from crewai import Task
from crewai.tasks.conditional_task import ConditionalTask
from crewai.tasks.task_output import TaskOutput
import logging

logger = logging.getLogger(__name__)

class GPSEConditionalTasks:
    """Quality control tasks for GPSE workflow"""
    
    @staticmethod
    def needs_more_news_sources(output: TaskOutput) -> bool:
        """Check if we have enough quality news sources"""
        try:
            # Check if output has articles
            if hasattr(output, 'pydantic') and hasattr(output.pydantic, 'articles'):
                articles = output.pydantic.articles
            else:
                # Try to extract from raw output
                articles = output.raw.get('articles', []) if isinstance(output.raw, dict) else []
            
            # Count high-quality articles
            high_quality = [a for a in articles if a.get('credibility', 0) >= 0.7]
            
            logger.info(f"Found {len(high_quality)} high-quality articles out of {len(articles)} total")
            
            # Need at least 10 high-quality sources
            return len(high_quality) < 10
            
        except Exception as e:
            logger.error(f"Error checking news sources: {e}")
            return True  # Retry on error
    
    @staticmethod
    def needs_deeper_analysis(output: TaskOutput) -> bool:
        """Check if strategic analysis is comprehensive enough"""
        try:
            # Check analysis depth metrics
            if hasattr(output, 'pydantic'):
                historical_matches = getattr(output.pydantic, 'historical_matches', 0)
                observations = getattr(output.pydantic, 'primary_observations', [])
            else:
                historical_matches = output.raw.get('historical_matches', 0)
                observations = output.raw.get('primary_observations', [])
            
            # Need at least 3 historical references and 4 observations
            needs_more = historical_matches < 3 or len(observations) < 4
            
            logger.info(f"Analysis check: {historical_matches} historical matches, {len(observations)} observations")
            
            return needs_more
            
        except Exception as e:
            logger.error(f"Error checking analysis depth: {e}")
            return False  # Don't retry on check error
    
    @staticmethod
    def validation_failed(output: TaskOutput) -> bool:
        """Check if document validation failed"""
        try:
            # Check for validation errors in output
            if isinstance(output.raw, str):
                return "error" in output.raw.lower() or "failed" in output.raw.lower()
            
            return False
            
        except Exception as e:
            logger.error(f"Error in validation check: {e}")
            return True

def create_conditional_tasks(agents_config: dict, tasks_config: dict) -> Dict[str, ConditionalTask]:
    """Create conditional tasks for quality control"""
    
    conditional_tasks = {}
    
    # Additional news gathering if insufficient sources
    conditional_tasks['additional_news_gathering'] = ConditionalTask(
        description="""
        Conduct additional news searches with broader queries:
        1. Expand search terms to include related topics
        2. Use different date ranges (last 72 hours)
        3. Include regional news sources
        4. Search for official statements and press releases
        
        Focus on finding authoritative sources that were missed in the initial search.
        """,
        expected_output="Additional 10-15 high-quality news articles from authoritative sources",
        agent=agents_config.get('news_scout'),  # Will be assigned actual agent instance
        condition=GPSEConditionalTasks.needs_more_news_sources
    )
    
    # Deeper historical analysis if needed
    conditional_tasks['deeper_historical_analysis'] = ConditionalTask(
        description="""
        Perform deeper historical analysis:
        1. Expand search to 6-month historical window
        2. Look for analogous situations in different regions
        3. Analyze actor behavior patterns over time
        4. Identify precedent cases and their outcomes
        
        Ensure at least 5 relevant historical references are found and analyzed.
        """,
        expected_output="Enhanced analysis with additional historical context and patterns",
        agent=agents_config.get('strategy_analyst'),  # Will be assigned actual agent instance
        condition=GPSEConditionalTasks.needs_deeper_analysis
    )
    
    # Retry document formatting if validation failed
    conditional_tasks['retry_document_formatting'] = ConditionalTask(
        description="""
        Retry document formatting with validation:
        1. Ensure all required sections are present
        2. Verify markdown formatting is correct
        3. Check that all metadata fields are populated
        4. Validate filename follows naming convention
        
        Fix any errors found and produce a valid document.
        """,
        expected_output="Properly formatted and validated GPSE strategic document",
        agent=agents_config.get('comms_archival'),  # Will be assigned actual agent instance
        condition=GPSEConditionalTasks.validation_failed
    )
    
    return conditional_tasks

# Integration with main crew
def integrate_conditional_tasks(crew_instance):
    """Integrate conditional tasks into the crew workflow"""
    
    # Get agents and tasks from crew
    agents = {agent.role: agent for agent in crew_instance.agents}
    tasks = crew_instance.tasks
    
    # Create conditional tasks
    conditional_configs = {
        'news_scout': agents.get('Expert Global News Researcher'),
        'strategy_analyst': agents.get('Lead Strategy Analyst'),
        'comms_archival': agents.get('Communications & Archival Lead')
    }
    
    conditional_tasks = create_conditional_tasks(conditional_configs, {})
    
    # Insert conditional tasks after their parent tasks
    enhanced_tasks = []
    
    for task in tasks:
        enhanced_tasks.append(task)
        
        # Add conditional task after news scouting
        if "news articles" in task.description and "additional_news_gathering" in conditional_tasks:
            enhanced_tasks.append(conditional_tasks['additional_news_gathering'])
        
        # Add conditional task after strategic analysis
        elif "strategic analysis" in task.description and "deeper_historical_analysis" in conditional_tasks:
            enhanced_tasks.append(conditional_tasks['deeper_historical_analysis'])
        
        # Add conditional task after document formatting
        elif "Format the strategic analysis" in task.description and "retry_document_formatting" in conditional_tasks:
            enhanced_tasks.append(conditional_tasks['retry_document_formatting'])
    
    # Update crew tasks
    crew_instance.tasks = enhanced_tasks
    
    logger.info(f"Enhanced crew with {len(conditional_tasks)} conditional tasks")
    
    return crew_instance

# Quality metrics tracking
class QualityMetrics:
    """Track quality metrics across runs"""
    
    def __init__(self):
        self.metrics = {
            'total_runs': 0,
            'successful_runs': 0,
            'retry_counts': {},
            'average_sources': 0,
            'average_processing_time': 0
        }
    
    def track_run(self, result: Any, duration: float):
        """Track metrics for a run"""
        self.metrics['total_runs'] += 1
        
        if result and not isinstance(result, Exception):
            self.metrics['successful_runs'] += 1
        
        # Update processing time
        current_avg = self.metrics['average_processing_time']
        self.metrics['average_processing_time'] = (
            (current_avg * (self.metrics['total_runs'] - 1) + duration) / 
            self.metrics['total_runs']
        )
    
    def get_success_rate(self) -> float:
        """Calculate success rate"""
        if self.metrics['total_runs'] == 0:
            return 0.0
        return self.metrics['successful_runs'] / self.metrics['total_runs']
    
    def report(self) -> str:
        """Generate metrics report"""
        return f"""
Quality Metrics Report:
- Total Runs: {self.metrics['total_runs']}
- Successful Runs: {self.metrics['successful_runs']}
- Success Rate: {self.get_success_rate():.2%}
- Average Processing Time: {self.metrics['average_processing_time']:.2f} seconds
"""
