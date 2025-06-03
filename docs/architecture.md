# GPSE Architecture Documentation

## System Overview

The Geopolitical Grand Strategy Engine (GPSE) is a multi-agent AI system built on CrewAI that analyzes global geopolitical developments and produces strategic intelligence briefs. The system uses a pipeline architecture with three specialized agents working in sequence.

## Core Components

### 1. Multi-Agent Framework (CrewAI)

GPSE leverages CrewAI's sequential processing model where agents pass information through a defined workflow:

```
News Scout → Strategic Analyst → Communicator → Output
```

Each agent has:
- **Specific Role**: Defined expertise area
- **Goal**: Clear objective for task completion
- **Tools**: Access to specific functions
- **Memory**: Enabled for context retention across runs

### 2. Agent Specifications

#### News Scout Agent
- **Role**: Information Curation Specialist
- **Responsibility**: Gather and filter geopolitical news from the last 24-48 hours
- **Key Capabilities**:
  - Multi-source news aggregation
  - Duplicate removal
  - Strategic relevance filtering
  - Source attribution
- **Tools Used**:
  - `enhanced_news_search`: Queries Tavily and World News APIs
  - `aggregate_geopolitical_news`: Combines and deduplicates results
  - `fetch_news_from_url`: Extracts full article content

#### Strategic Analyst Agent
- **Role**: Lead Strategy Analyst
- **Responsibility**: Apply strategic frameworks to current events
- **Key Capabilities**:
  - Historical pattern analysis
  - Strategic framework application
  - Scenario generation
  - Risk assessment
- **Tools Used**:
  - `query_strategy_database`: Searches ChromaDB for historical context
  - `enhanced_news_search`: Additional fact-checking

#### Communicator Agent
- **Role**: Communications & Archival Lead
- **Responsibility**: Transform analysis into professional intelligence products
- **Key Capabilities**:
  - Document structuring
  - Quality control
  - Archival management
- **Tools Used**:
  - Document generation (built-in)
  - File system operations

### 3. Data Storage

#### ChromaDB Vector Database
- **Purpose**: Store and retrieve historical analyses
- **Implementation**: Local persistent storage
- **Windows Fixes**: 
  - Short path (`C:\gpse_data`)
  - Local segment manager
  - Custom SQLite temp directory

#### File System
- **Output Directory**: `strategy_analyses/`
- **Naming Convention**: `GGSM-[Date]-DailyAnalysis.md`
- **Format**: Markdown for readability and portability

### 4. External Integrations

#### News APIs
1. **Tavily API**
   - Primary news search
   - 1000 searches/month (free tier)
   - High-quality relevance ranking

2. **World News API**
   - Secondary source
   - Additional geographic coverage
   - Fallback option

3. **Serper API** (Optional)
   - Google search results
   - Enhanced coverage

#### Language Model
- **Provider**: OpenAI
- **Model**: GPT-4o (recommended)
- **Usage**: Agent reasoning and analysis
- **Configuration**: Via environment variables

## Data Flow

### 1. Input Phase
```
External APIs → News Scout Agent
    ↓
    Tavily API ──┐
    World News ──┼→ enhanced_news_search()
    Serper API ──┘
    ↓
    aggregate_geopolitical_news()
    ↓
    Filtered News Summary
```

### 2. Analysis Phase
```
News Summary → Strategic Analyst Agent
    ↓
    query_strategy_database() ← ChromaDB
    ↓
    Apply Strategic Frameworks
    ├── Power Competition Analysis
    ├── Risk Assessment
    ├── Trend Identification
    └── Scenario Planning
    ↓
    Strategic Analysis Document
```

### 3. Output Phase
```
Strategic Analysis → Communicator Agent
    ↓
    Document Structuring
    ├── Executive Summary
    ├── Critical Developments
    ├── Strategic Assessment
    └── Recommendations
    ↓
    Quality Control
    ↓
    Save to File System & Archive to ChromaDB
```

## Key Design Decisions

### 1. Sequential Processing
- **Rationale**: Ensures each agent completes its task before passing to the next
- **Benefits**: Clear data flow, easier debugging, predictable outputs
- **Trade-off**: Longer processing time vs parallel execution

### 2. Tool Specialization
- **Rationale**: Each agent has access only to tools needed for its role
- **Benefits**: Security, focused functionality, cleaner architecture
- **Example**: Only News Scout can search news; only Analyst can query history

### 3. Memory System
- **Implementation**: CrewAI's built-in memory with ChromaDB backend
- **Benefits**: Context retention, learning from past analyses
- **Windows Fix**: Custom environment variables prevent permission errors

### 4. Markdown Output
- **Rationale**: Human-readable, version-control friendly, portable
- **Benefits**: Easy to read, share, and process
- **Structure**: Consistent sections for automated parsing

## Error Handling

### 1. API Failures
- **Strategy**: Graceful degradation
- **Implementation**: Try multiple sources, continue with available data
- **User Notification**: Warnings in output about missing sources

### 2. ChromaDB Issues
- **Primary Fix**: Windows-specific environment variables
- **Fallback**: System continues without historical context
- **Recovery**: Automatic retry on next run

### 3. Rate Limiting
- **Detection**: API response codes
- **Handling**: Exponential backoff
- **User Guidance**: Clear error messages with solutions

## Performance Characteristics

### Typical Execution Time
- **News Gathering**: 1-2 minutes
- **Analysis**: 2-3 minutes
- **Document Generation**: 1 minute
- **Total**: 4-6 minutes

### Resource Usage
- **Memory**: ~500MB during execution
- **Storage**: ~10MB per analysis
- **Network**: ~50 API calls per run

### Scalability Considerations
- **Current**: Single-threaded sequential processing
- **Future**: Could parallelize news gathering
- **Limitation**: API rate limits are the primary constraint

## Security Considerations

### 1. API Key Management
- **Storage**: Local `.env` file
- **Access**: Environment variables only
- **Rotation**: Manual process required

### 2. Data Privacy
- **Sources**: Public news only
- **Storage**: Local file system
- **Transmission**: HTTPS for all API calls

### 3. Output Security
- **Classification**: Unclassified open-source intelligence
- **Distribution**: User-controlled
- **Retention**: Indefinite local storage

## Future Architecture Enhancements

### 1. Web Interface
- **Technology**: FastAPI + React
- **Benefits**: Easier access, better visualization
- **Challenge**: Deployment complexity

### 2. Distributed Processing
- **Approach**: Celery task queue
- **Benefits**: Faster execution, better reliability
- **Challenge**: Infrastructure requirements

### 3. Enhanced Memory
- **Approach**: Fine-tuned embeddings
- **Benefits**: Better historical recall
- **Challenge**: Computational requirements

## Monitoring and Maintenance

### 1. Logging
- **Level**: INFO by default
- **Location**: Console output
- **Format**: Timestamp, component, message

### 2. Health Checks
- **API Connectivity**: Pre-flight checks
- **Database Access**: Startup verification
- **Output Validation**: Post-generation checks

### 3. Maintenance Tasks
- **Database Cleanup**: Manual, as needed
- **Log Rotation**: Not implemented
- **Backup**: User responsibility

---

## Diagram References

For visual representations of the architecture:
- [System Architecture](diagrams/system_architecture.mermaid)
- [Data Flow](diagrams/data_flow.mermaid)
- [Agent-Tool Mapping](diagrams/agent_tools_mapping.mermaid)
