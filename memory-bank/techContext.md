# GPSE Technical Context

## Technology Stack

### Core Languages & Frameworks
- **Python 3.x** - Primary development language
- **CrewAI** - Multi-agent orchestration framework
- **ChromaDB** - Vector database for embeddings storage
- **Sentence Transformers** - Embedding generation

### Key Dependencies
```
chromadb==0.5.23
sentence-transformers==2.7.0
crewai (version TBD)
python-dotenv (for environment management)
```

### Additional Libraries (Planned)
- `openai` - For GPT model API access
- `anthropic` - For Claude model API access
- `requests` - For news API interactions
- `tavily-python` - For Tavily API integration
- `schedule` or `cron` - For daily automation

## API Integrations

### News Data Sources
1. **Primary News APIs** (Choose one or more):
   - NewsAPI.org
   - World News API
   - Newsdata.io
   - Each requires API key
   - Rate limits vary by provider

2. **Tavily API**
   - AI-optimized web research
   - Enhanced entity search
   - Requires API key
   - Used for supplementary research

### LLM APIs

#### Production Models
1. **Claude 4 Opus (Anthropic)**
   - Used by: Lead Strategy Analyst
   - Purpose: Complex strategic analysis
   - API Key: `ANTHROPIC_API_KEY`

2. **GPT-4 Turbo (OpenAI)**
   - Alternative to Claude 4
   - Used by: Lead Strategy Analyst
   - API Key: `OPENAI_API_KEY`

3. **GPT-3.5-Turbo (OpenAI)**
   - Used by: Information Curation, Communications agents
   - Purpose: Lower-complexity tasks
   - Cost-effective option

#### Local Model Options (via LM Studio)
- **Mistral 7B** - Efficient general-purpose model
- **Llama 3 8B** - Strong performance for size
- Used for: Cost reduction, offline capability, data privacy

## Development Environment

### IDE & Tools
- **VS Code** - Primary development environment
- **Git** - Version control
- **Python Virtual Environment** - `gpse_venv/`

### Project Structure
```
GPSE_Project/
├── .env                    # API keys and secrets (gitignored)
├── .gitignore             # Version control exclusions
├── requirements.txt       # Python dependencies
├── db_manager.py         # ChromaDB interface
├── gpse_tools.py         # Utility functions
├── memory-bank/          # Project documentation
│   ├── projectbrief.md
│   ├── productContext.md
│   ├── systemPatterns.md
│   ├── techContext.md
│   ├── activeContext.md
│   └── progress.md
├── strategy_analyses/    # Generated analysis documents
│   └── GGSM-*.md
├── strategy_db_chroma/   # ChromaDB persistent storage
└── gpse_venv/           # Python virtual environment
```

### Environment Variables
Required in `.env` file:
```
# LLM API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# News API Keys (at least one required)
NEWS_API_KEY=your_newsapi_key
WORLD_NEWS_API_KEY=your_world_news_key
NEWSDATA_API_KEY=your_newsdata_key

# Research API
TAVILY_API_KEY=your_tavily_key

# Optional Configuration
ENVIRONMENT=development
LLM_PROVIDER=anthropic  # or 'openai'
LOCAL_MODEL_ENDPOINT=http://localhost:1234/v1  # LM Studio endpoint
```

## Model Specifications

### Embedding Model
- **Model:** all-MiniLM-L6-v2
- **Dimensions:** 384
- **Use Case:** Converting text to vector embeddings
- **Performance:** Fast, suitable for real-time operations
- **Storage:** ~25MB model size

### Vector Database Configuration
- **ChromaDB Settings:**
  - Persistence: Enabled
  - Path: `./strategy_db_chroma`
  - Collection: `grand_strategy`
  - Distance Function: Cosine similarity (default)

## Security Considerations

### API Key Management
- All keys stored in `.env` file
- `.env` is gitignored to prevent accidental commits
- Keys never hardcoded in source files
- Environment variable access via `os.environ` or `python-dotenv`

### Data Security
- ChromaDB stored locally (no cloud sync)
- Analysis documents contain sensitive geopolitical assessments
- Access controlled at filesystem level
- No public-facing endpoints

### Network Security
- All API calls use HTTPS
- Consider VPN for sensitive deployments
- Rate limiting to prevent API abuse
- Error handling to avoid key exposure in logs

## Performance Considerations

### API Rate Limits
- **OpenAI:** Varies by tier, typically 10,000 TPM for GPT-3.5
- **Anthropic:** Varies by tier, monitor usage
- **News APIs:** Usually 100-1000 requests/day on free tiers
- **Tavily:** Check current limits

### Processing Times
- **Embedding Generation:** ~1-2 seconds per document
- **ChromaDB Query:** Sub-second for most queries
- **LLM API Calls:** 5-30 seconds depending on complexity
- **Full Daily Run:** Estimated 5-15 minutes

### Storage Requirements
- **ChromaDB:** ~1GB per 100,000 documents
- **Analysis Documents:** ~10-50KB each
- **Daily Growth:** ~500KB-1MB with embeddings

## Development Best Practices

### Code Quality
- Type hints for all functions
- Comprehensive docstrings
- Error handling and logging
- Unit tests for critical functions

### Git Workflow
- Feature branches for new development
- Descriptive commit messages
- Regular commits
- Never commit sensitive data

### Testing Strategy
- Unit tests for utility functions
- Integration tests for API interactions
- Mock external services in tests
- Manual validation of generated analyses

### Monitoring & Logging
- Structured logging with levels
- API call tracking
- Error aggregation
- Performance metrics
