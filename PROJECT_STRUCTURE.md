# GPSE Project Structure - Consolidated Version

## Core Files

### 1. **main_crew.py**
- Main orchestration file for the GPSE crew
- Contains `GPSECrewFixedFinal` class with all fixes applied
- Handles the three-agent workflow: News Scout → Geo Analyst → Communicator
- Includes fixes for:
  - Double path issue (strategy_analyses/strategy_analyses/...)
  - Missing analysis_id KeyError
  - Result logging errors
  - Context window optimization

### 2. **gpse_tools.py**
- Enhanced news gathering and analysis tools
- Contains:
  - `enhanced_news_search()` - Tavily API integration
  - `fetch_news_from_url()` - Direct URL content extraction
  - `aggregate_geopolitical_news()` - Multi-topic news aggregation
  - `query_strategy_database()` - ChromaDB query interface
  - Helper functions: `get_date_code()`, `get_timestamp()`, etc.

### 3. **communicator_agent_implementation.py**
- Specialized tools for the Communicator agent
- Contains:
  - `FileWriterTool` - Saves formatted analysis to disk
  - `StrategyDBUpdateTool` - Updates ChromaDB with new analyses
  - `create_communicator_agent()` - Factory function for the agent

### 4. **db_manager.py**
- ChromaDB management and initialization
- Handles document processing and vector storage
- Provides persistent storage for historical analyses

### 5. **run_gpse.py**
- Terminal-friendly runner script
- Provides all required date variables
- Handles errors gracefully
- Shows clear success/failure indicators

## Execution

### PowerShell (Recommended)
```powershell
cd C:\Users\every\Desktop\GPSE_Project
.\run_gpse.ps1
```

### Direct Python
```powershell
cd C:\Users\every\Desktop\GPSE_Project
.\gpse_venv\Scripts\Activate.ps1
python run_gpse.py
```

## Configuration Files

- **config/agents.yaml** - Agent role definitions
- **config/tasks_simplified.yaml** - Task configurations
- **.env** - API keys and environment settings

## Output

- **strategy_analyses/** - Generated GGSM analysis files
- **logs/** - Execution logs with timestamps
- **strategy_db_chroma/** - ChromaDB persistent storage

## Memory Bank

- **memory-bank/** - Project documentation and context
  - projectbrief.md
  - productContext.md
  - systemPatterns.md
  - techContext.md
  - activeContext.md
  - progress.md

## Archive

- **archive/** - Old versions and experimental files (for reference)

## Key Features

1. **Three-Agent System**:
   - News Scout: Gathers geopolitical news using multiple APIs
   - Geo Analyst: Analyzes news with historical context
   - Communicator: Formats and saves the analysis

2. **Context Window Management**:
   - Optimized prompts to stay under token limits
   - Uses GPT-4 Turbo (128k) and GPT-3.5 Turbo (16k)
   - Progressive memory summarization

3. **Error Handling**:
   - Graceful failure recovery
   - Clear logging and status reporting
   - File verification after execution

4. **Historical Context**:
   - ChromaDB integration for semantic search
   - Builds on previous analyses
   - Maintains institutional memory
