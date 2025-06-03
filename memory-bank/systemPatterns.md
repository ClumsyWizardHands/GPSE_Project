# GPSE System Patterns

## Architecture Overview

### CrewAI Multi-Agent System
The system employs three specialized AI agents working in sequence:

1. **Information Curation Specialist**
   - Role: News gathering and initial processing
   - Model: GPT-3.5-Turbo or local models (Mistral 7B, Llama 3 8B)
   - Responsibilities:
     - Query news APIs for relevant global political events
     - Perform supplementary searches via Tavily API
     - Pre-filter and summarize raw news data
     - Prepare structured input for analysis

2. **Lead Strategy Analyst**
   - Role: Deep analysis and strategic synthesis
   - Model: Claude 4 Opus or GPT-4 Turbo
   - Responsibilities:
     - Query ChromaDB for relevant historical context
     - Analyze new information against historical patterns
     - Generate comprehensive strategic assessments
     - Identify trends, risks, and opportunities

3. **Communications & Archival Lead**
   - Role: Documentation and knowledge management
   - Model: GPT-3.5-Turbo or local models
   - Responsibilities:
     - Format analysis into standardized documents
     - Save new analyses with proper naming conventions
     - Add new content to ChromaDB with embeddings
     - Maintain analysis archive integrity

## Data Flow Patterns

### Processing Pipeline
```
External APIs → Information Curation → Context Retrieval → Strategic Analysis → Documentation → Archival
     ↓                                        ↓                                         ↓
News Sources                            ChromaDB Query                            New Document
Tavily Search                          Historical Data                          Update ChromaDB
```

### Vector Storage Pattern
- **Embedding Model:** all-MiniLM-L6-v2 (sentence-transformers)
- **Database:** ChromaDB with persistent storage
- **Collection:** 'grand_strategy'
- **Chunking Strategy:** Section-based (Executive Summary, Country Analyses, Scenarios)
- **Document IDs:** Format: `{base_id}-{section_type}` (e.g., `GGSM-052825-china-analysis`)

## Naming Conventions

### Strategy Documents
- **Filename Pattern:** `STRATEGY-MMDDYY-Description.md`
- **Example:** `GGSM-052825-GlobalOutlook.md`
- **Components:**
  - STRATEGY: 4-character strategy code (e.g., GGSM)
  - MMDDYY: Date in month-day-year format
  - Description: Brief descriptor of focus area

### Document Structure
```markdown
---
## Geopolitical Grand Strategy Monitor
**Strategic Synthesis Entry**
**Date:** [Full Date]
**Entry ID:** [STRATEGY-MMDDYY-Description]

### Executive Summary
[High-level synthesis]

### Primary Observations
#### 1. **[Country/Actor]: [Theme]**
* *Observable Behavior:*
* *Inferred Strategic Shift:*
* *Emotion Signals/Identity/Resentments:*

### Scenario Implications
[Strategic implications and risks]
---
```

### Database Entry IDs
- **Format:** `GPSE_YYYY-MM-DD_NNN` or `{document_id}-{chunk_type}`
- **Examples:**
  - `GPSE_2025-06-02_001`
  - `GGSM-052825-executive-summary`
  - `GGSM-052825-russia-analysis`

## Key Design Decisions

### Modularity
- Each agent has a single, well-defined responsibility
- Tools (ChromaDB operations, API calls) are separate from agent logic
- Document processing is chunked for better retrieval

### Scalability Considerations
- Local vector database (ChromaDB) for data sovereignty
- Chunked storage allows granular retrieval
- API-based LLMs allow model switching without code changes

### Error Handling Patterns
- Graceful degradation if APIs are unavailable
- Fallback to cached/historical data when possible
- Comprehensive logging for debugging and audit trails

### Security Patterns
- API keys stored in `.env` file
- `.env` excluded from version control
- Local database storage (no cloud dependencies)
- Controlled access to output documents

## Integration Points

### External Services
1. **News APIs** (Multiple providers for redundancy)
   - Primary sources for current events
   - Rate limiting considerations
   - Response caching where appropriate

2. **Tavily API**
   - AI-optimized supplementary research
   - Entity and event investigation
   - Broader context gathering

3. **LLM APIs**
   - OpenAI (GPT-3.5, GPT-4)
   - Anthropic (Claude 4)
   - Local models via LM Studio

### Internal Components
1. **ChromaDB Interface** (`db_manager.py`)
   - Standardized add/query operations
   - Embedding generation
   - Collection management

2. **Utility Tools** (`gpse_tools.py`)
   - File operations
   - Date/time formatting
   - Text processing
   - Validation functions

## Constraints and Boundaries

### Technical Constraints
- Daily batch processing (not real-time)
- API rate limits and costs
- Local storage capacity for vector database
- LLM context window limitations

### Design Constraints
- Single-user system (not multi-tenant)
- Sequential processing (not parallel)
- Document-based output (not interactive)
- English language focus

### Operational Constraints
- Manual API key management
- Daily scheduling requires external trigger
- No built-in backup/recovery (rely on git)
- Limited to political domain analysis
