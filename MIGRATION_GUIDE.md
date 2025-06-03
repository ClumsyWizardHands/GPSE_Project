# GPSE Migration Guide: From main_crew.py to gpse_crew.py

## What's Been Implemented

### 1. **CrewBase Pattern** (gpse_crew.py)
- ✅ Uses @CrewBase decorator for cleaner architecture
- ✅ YAML configuration loading from config files
- ✅ Proper lifecycle hooks (@before_kickoff, @after_kickoff)
- ✅ Automatic agent/task collection via decorators

### 2. **Resilient Tools with Retry Logic**
- ✅ ResilientTool base class with exponential backoff
- ✅ TavilyNewsSearchTool - AI-optimized news search
- ✅ NewsAPITool - Traditional news API integration
- ✅ ChromaDBQueryTool - Historical analysis retrieval
- ✅ ValidateSourcesTool - Source credibility checking

### 3. **Conditional Tasks** (gpse_conditional_tasks.py)
- ✅ Quality control checks for news sources
- ✅ Depth validation for strategic analysis
- ✅ Document validation and retry
- ✅ Quality metrics tracking

### 4. **Configuration Files**
- ✅ config/agents.yaml - All agent definitions
- ✅ config/tasks.yaml - Task pipeline with context

## Quick Start

### 1. Install Updated Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test Your Setup
```bash
python test_gpse_crew.py
```

### 3. Run the New Implementation
```bash
python gpse_crew.py
```

## Key Differences from main_crew.py

### Old Pattern:
```python
# Direct agent creation
news_scout_agent = Agent(
    role="News Scout",
    goal="Find news",
    backstory="...",
    tools=[tool1, tool2],
    llm=llm
)
```

### New Pattern:
```python
@agent
def news_scout(self) -> Agent:
    return Agent(
        config=self.agents_yaml['news_scout'],
        tools=[TavilyNewsSearchTool(), NewsAPITool()],
        llm=self.efficient_llm,
        max_iter=3,
        allow_delegation=False
    )
```

## Features Added

### 1. **Smart LLM Selection**
- GPT-3.5 for news gathering (cost-effective)
- GPT-4/Claude for strategic analysis (powerful)
- Automatic fallback if Anthropic key not available

### 2. **Error Handling**
- 3x retry with exponential backoff on API failures
- Graceful degradation when services unavailable
- Comprehensive logging throughout

### 3. **Quality Control**
- Minimum 10 high-quality sources required
- Source credibility validation (>0.7 score)
- Historical context requirements (3+ references)
- Automatic retry if quality thresholds not met

### 4. **Memory and Context**
- Crew memory enabled for better continuity
- Task context properly configured
- Historical pattern analysis integrated

## Configuration Options

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_key
TAVILY_API_KEY=your_key

# Optional but recommended
ANTHROPIC_API_KEY=your_key  # For Claude
NEWS_API_KEY=your_key       # For NewsAPI
```

### Customization Points

1. **Adjust Quality Thresholds** (gpse_conditional_tasks.py):
   ```python
   # Line 30: Minimum articles required
   return len(high_quality) < 10  # Change threshold
   
   # Line 27: Credibility threshold
   high_quality = [a for a in articles if a.get('credibility', 0) >= 0.7]
   ```

2. **Change LLM Models** (gpse_crew.py):
   ```python
   # Line 81: Efficient model
   model="gpt-3.5-turbo"  # Could use gpt-4o-mini
   
   # Line 95: Powerful model
   model="gpt-4-turbo-preview"  # Could use gpt-4o
   ```

3. **Modify Retry Logic** (gpse_crew.py):
   ```python
   # Line 264: Max retries
   max_retries = 3  # Increase for more reliability
   ```

## Testing Without API Costs

The test script includes a minimal run test that's commented out to avoid API costs:
```python
# Line 135 in test_gpse_crew.py
# result = enhanced_crew.kickoff(inputs=test_inputs)
```

Uncomment this line when ready to test with real API calls.

## Monitoring and Metrics

The new implementation includes quality metrics tracking:
```python
from gpse_conditional_tasks import QualityMetrics

metrics = QualityMetrics()
# After each run:
metrics.track_run(result, duration)
print(metrics.report())
```

## Troubleshooting

### Import Errors
- Ensure virtual environment is activated
- Run: `pip install -r requirements.txt`

### API Key Errors
- Check .env file has all required keys
- Verify keys are valid and have credits

### ChromaDB Errors
- Delete strategy_db_chroma folder to reset
- Check disk space availability

## Next Steps

1. **Run Tests**: `python test_gpse_crew.py`
2. **Review Logs**: Check logs/ directory for detailed output
3. **First Run**: `python gpse_crew.py` (will cost ~$0.50-$2)
4. **Schedule**: Set up cron job for daily execution
5. **Monitor**: Track quality metrics and costs

## Advanced Usage

### Adding Custom Tools
```python
class MyCustomTool(ResilientTool):
    name: str = "My Tool"
    description: str = "Tool description"
    
    def _run(self, input: str) -> str:
        def execute():
            # Your tool logic here
            return result
        return self._run_with_retry(execute)
```

### Modifying Task Flow
Edit config/tasks.yaml to:
- Change task descriptions
- Modify expected outputs
- Add task dependencies via context
- Specify output files

The new implementation is production-ready with significant improvements in reliability, maintainability, and cost optimization.
