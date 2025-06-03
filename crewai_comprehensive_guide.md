# Comprehensive CrewAI Guide for GPSE Project

Based on the documentation gathered from Context7 and Firecrawl, here's a comprehensive guide to improve our GPSE implementation.

## Key Concepts and Best Practices

### 1. Project Structure
The recommended CrewAI project structure is:
```
project_name/
├── .env
├── src/
│   └── project_name/
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       ├── crew.py
│       ├── tools.py
│       └── main.py
├── output/
└── requirements.txt
```

### 2. Using YAML Configuration Files
Instead of defining agents and tasks directly in Python, CrewAI recommends using YAML files:

**agents.yaml example:**
```yaml
researcher:
  role: >
    {topic} Senior Data Researcher
  goal: >
    Uncover cutting-edge developments in {topic}
  backstory: >
    You're a seasoned researcher with a knack for uncovering the latest
    developments in {topic}. Known for your ability to find the most relevant
    information and present it in a clear and concise manner.
```

**tasks.yaml example:**
```yaml
research_task:
  description: >
    Conduct a thorough research about {topic}
  expected_output: >
    A list with 10 bullet points of the most relevant information about {topic}
  agent: researcher
  output_file: output/research.md
```

### 3. Using CrewAI Decorators
The modern approach uses decorators for cleaner code:

```python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class GPSECrew():
    """GPSE crew"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            verbose=True,
            tools=[SerperDevTool()]
        )
    
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task']
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # Automatically created by @agent decorator
            tasks=self.tasks,    # Automatically created by @task decorator
            process=Process.sequential,
            verbose=True
        )
```

### 4. Task Context and Dependencies
Tasks can have context from other tasks:

```python
# Method 1: Direct context assignment
task3.context = [task1, task2]

# Method 2: In YAML
reporting_task:
  description: >
    Create a report based on research
  agent: reporter
  context:
    - research_task
    - analysis_task
```

### 5. Process Types

**Sequential Process** (default):
```python
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    process=Process.sequential
)
```

**Hierarchical Process** (with manager):
```python
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    process=Process.hierarchical,
    manager_llm="gpt-4o"  # or manager_agent=my_manager
)
```

### 6. Memory and Collaboration

Enable memory for better context retention:
```python
crew = Crew(
    agents=agents,
    tasks=tasks,
    memory=True  # Enables memory
)
```

Enable delegation for agent collaboration:
```python
agent = Agent(
    role="Researcher",
    goal="Research topics",
    backstory="Expert researcher",
    allow_delegation=True  # Can delegate to other agents
)
```

### 7. Advanced Features

**Conditional Tasks:**
```python
from crewai.tasks.conditional_task import ConditionalTask

def should_run_task(output: TaskOutput) -> bool:
    return len(output.pydantic.events) < 10

conditional_task = ConditionalTask(
    description="Additional processing if needed",
    condition=should_run_task,
    agent=processor_agent
)
```

**Human Input:**
```python
task = Task(
    description="Analyze data and confirm with human",
    agent=analyst,
    human_input=True  # Will prompt for human input
)
```

**Async Execution:**
```python
task = Task(
    description="Background processing",
    agent=processor,
    async_execution=True
)
```

### 8. CrewAI Flows (for structured workflows)

```python
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

class WorkflowState(BaseModel):
    input_data: str = ""
    processed_data: str = ""
    final_output: str = ""

class DataFlow(Flow[WorkflowState]):
    @start()
    def process_input(self):
        # Initial processing
        self.state.processed_data = process(self.state.input_data)
    
    @listen(process_input)
    def generate_output(self):
        # Use crew for complex processing
        result = crew.kickoff(inputs={'data': self.state.processed_data})
        self.state.final_output = result.raw
```

## Improvements for GPSE Project

### 1. Migrate to YAML Configuration

Create `config/agents.yaml`:
```yaml
news_scout:
  role: >
    Expert Global News Researcher
  goal: >
    Discover and compile the most recent and significant news articles 
    regarding specified global political topics from the last 24-48 hours
  backstory: >
    A diligent news analyst specializing in identifying pivotal geopolitical 
    events with deep expertise in conflict analysis and international relations

info_curator:
  role: >
    Information Curation Specialist
  goal: >
    Gather and synthesize recent global political news and events from multiple sources
  backstory: >
    You are an expert information analyst specializing in global political affairs.
    Your role is to efficiently gather, filter, and pre-process news from various 
    sources to identify the most significant geopolitical developments

strategy_analyst:
  role: >
    Lead Strategy Analyst
  goal: >
    Produce comprehensive strategic analyses by synthesizing current events 
    with historical context
  backstory: >
    You are a senior geopolitical strategist with decades of experience analyzing
    international relations, state behavior, and strategic trends

comms_archival:
  role: >
    Communications & Archival Lead
  goal: >
    Format analyses into standardized documents and maintain the knowledge base
  backstory: >
    You are responsible for transforming strategic analyses into clear, actionable
    documents following established formats
```

Create `config/tasks.yaml`:
```yaml
news_scout_task:
  description: >
    Search for top news articles from the last 24-48 hours focusing on:
    1. Active warzones and battlefronts
    2. Strategic atrocities with geopolitical impact
    3. Major power alignments and support behaviors
    4. Proxy conflicts and covert escalations
    5. State-enabled cyber warfare and disinformation
  expected_output: >
    A structured report with URLs and extracted content for each article
  agent: news_scout

gather_news_task:
  description: >
    Synthesize findings from news scouting with additional research
  expected_output: >
    A comprehensive briefing with executive overview and detailed findings
  agent: info_curator
  context:
    - news_scout_task

analyze_strategy_task:
  description: >
    Conduct deep strategic analysis using historical context from database
  expected_output: >
    Comprehensive strategic analysis with trends and scenarios
  agent: strategy_analyst
  context:
    - gather_news_task

document_archive_task:
  description: >
    Format analysis and update ChromaDB knowledge base
  expected_output: >
    Confirmation of saved analysis and database update
  agent: comms_archival
  context:
    - analyze_strategy_task
  output_file: output/analysis.md
```

### 2. Implement CrewBase Pattern

```python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff

@CrewBase
class GPSECrew():
    """Geopolitical Grand Strategy Engine Crew"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @before_kickoff
    def prepare_analysis(self, inputs):
        """Prepare for analysis run"""
        inputs['timestamp'] = datetime.now()
        inputs['date_code'] = get_date_code()
        return inputs
    
    @after_kickoff
    def post_process(self, result):
        """Post-process results"""
        # Add to ChromaDB
        process_strategy_document(result.output_file)
        return result
    
    @agent
    def news_scout(self) -> Agent:
        return Agent(
            config=self.agents_config['news_scout'],
            tools=[self.news_search_tool, self.web_scraper_tool],
            llm=self.support_llm,
            allow_delegation=True
        )
    
    # ... other agents ...
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=True,
            verbose=True
        )
```

### 3. Add Error Handling and Retry Logic

```python
from crewai.agents.agent_builder.base_agent import BaseAgent

class ResilientAgent(BaseAgent):
    def execute_task(self, task):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return super().execute_task(task)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
```

### 4. Implement Conditional Tasks for Quality Control

```python
def needs_more_research(output: TaskOutput) -> bool:
    """Check if we have enough quality sources"""
    articles = output.pydantic.articles if hasattr(output.pydantic, 'articles') else []
    return len(articles) < 10 or any(a.quality_score < 0.7 for a in articles)

additional_research_task = ConditionalTask(
    description="Conduct additional research if initial results are insufficient",
    condition=needs_more_research,
    agent=news_scout,
    expected_output="Additional high-quality news sources"
)
```

### 5. Use Planning for Better Coordination

```python
crew = Crew(
    agents=agents,
    tasks=tasks,
    process=Process.sequential,
    planning=True,  # Enable planning
    planning_llm="gpt-4o"  # Use powerful model for planning
)
```

### 6. Implement Custom Tools with Result Validation

```python
from crewai_tools import BaseTool

class ValidatedTavilyTool(BaseTool):
    name: str = "Validated Tavily Search"
    description: str = "Search with quality validation"
    
    def _run(self, query: str) -> str:
        results = tavily_search(query)
        # Validate results
        validated = [r for r in results if self._validate_source(r)]
        if len(validated) < 3:
            # Retry with broader query
            results = tavily_search(f"{query} news analysis")
            validated.extend([r for r in results if self._validate_source(r)])
        return format_results(validated)
    
    def _validate_source(self, result):
        # Check source credibility, date, relevance
        return (
            result.get('date') >= datetime.now() - timedelta(days=2) and
            result.get('credibility_score', 0) > 0.6
        )
```

### 7. Implement Crew Training

```python
# Train the crew on historical data
crew.train(
    n_iterations=5,
    filename="gpse_crew_training.pkl",
    inputs={
        "focus_areas": ["Ukraine conflict", "Middle East tensions", "US-China relations"],
        "quality_threshold": 0.8
    }
)
```

## Testing Strategy

### Unit Tests for Tools
```python
def test_news_search_tool():
    tool = TavilyNewsSearchTool()
    results = tool._run("Ukraine Russia conflict")
    assert len(results) > 0
    assert all('url' in r for r in results)
```

### Integration Tests for Crew
```python
def test_full_analysis_pipeline():
    crew = GPSECrew().crew()
    result = crew.kickoff(inputs={"topic": "global conflicts"})
    assert result.success
    assert os.path.exists(result.output_file)
    assert len(result.raw) > 1000  # Substantial content
```

## Deployment Considerations

1. **Use CrewAI CLI for easier management:**
   ```bash
   crewai create crew gpse
   crewai install
   crewai run
   ```

2. **Environment-specific configurations:**
   ```python
   if os.getenv('ENVIRONMENT') == 'production':
       crew_config['verbose'] = False
       crew_config['memory'] = True
   ```

3. **Monitoring and Observability:**
   - Use callbacks for tracking execution
   - Log all API calls and costs
   - Monitor task completion times

This comprehensive guide incorporates best practices from the CrewAI documentation and should help improve the GPSE implementation significantly.
