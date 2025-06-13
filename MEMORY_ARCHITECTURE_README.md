# GPSE Memory Architecture Implementation

## Overview

The Geopolitical Grand Strategy Engine (GPSE) now includes a sophisticated memory architecture using ChromaDB to store and retrieve past analyses. This enables the system to build institutional knowledge over time, reference historical patterns, and track prediction accuracy.

## Phase 1 Implementation (Completed)

### Key Features

1. **Historical Context Integration**
   - System queries ChromaDB for relevant past analyses before generating new reports
   - Analyst receives both current news AND historical context
   - Enables pattern recognition across time periods

2. **Automatic Memory Storage**
   - Each new analysis is automatically chunked and stored in ChromaDB
   - Proper metadata tagging for date, section, and document ID
   - Enables future retrieval and reference

3. **Learning from Past Assessments**
   - New section in reports dedicated to historical continuity
   - References validated/invalidated predictions
   - Identifies recurring patterns and themes

### Architecture Components

#### 1. ChromaDB Integration
- **Database**: Local ChromaDB instance at `./strategy_db_chroma`
- **Collection**: `grand_strategy`
- **Embedding Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Chunking Strategy**: Section-based (Executive Summary, Country Analyses, Scenarios)

#### 2. Memory Workflow
```
1. News Collection → 
2. Historical Query (NEW) → 
3. Strategic Analysis (with context) → 
4. Report Generation → 
5. Memory Storage (NEW)
```

#### 3. Query Topics
The system queries historical data for these key areas:
- US China Russia strategic competition
- Taiwan Ukraine Middle East tensions
- Cyber warfare AI militarization
- Economic sanctions trade war
- Terrorism non-state actors
- UN Security Council
- Critical infrastructure
- Climate change conflicts

## Usage

### Running the Memory-Enabled System

```bash
# First, populate ChromaDB with existing analyses
python populate_chromadb.py

# Then run the memory-enabled GPSE
python run_gpse_improved_with_memory.py
```

### Key Files

- `run_gpse_improved_with_memory.py` - Main runner with memory integration
- `db_manager.py` - ChromaDB interface and utilities
- `populate_chromadb.py` - Tool to populate database with existing analyses

### Output Enhancements

Reports now include:
1. **Executive Summary** - With insights from historical patterns
2. **Learning from Past Assessments** - New dedicated section
3. **Historical References** - Throughout the analysis
4. **Pattern Recognition** - Across time periods

## Benefits

### 1. Continuity
- "As we predicted on June 8..."
- "This confirms our assessment from..."
- "Contrary to our previous analysis..."

### 2. Learning
- "Our confidence in X has increased because..."
- "Historical pattern suggests..."
- "Based on 3 similar past events..."

### 3. Pattern Recognition
- "This matches the pattern we identified in..."
- "Recurring theme across multiple analyses..."
- "Deviation from established pattern..."

### 4. Accountability
- Track prediction accuracy over time
- Identify which assessments proved correct
- Learn from analytical mistakes

## Future Phases

### Phase 2: Prediction Tracking (Planned)
- Extract specific predictions with timeframes
- Create prediction verification system
- Add accuracy metrics dashboard
- Confidence calibration based on track record

### Phase 3: Advanced Intelligence (Future)
- Pattern recognition algorithms
- Anomaly detection
- Predictive modeling
- Trend visualization

## Technical Details

### Database Schema
Each document chunk includes:
- `id`: Unique identifier (e.g., `GGSM-20250612-executive-summary`)
- `text`: The actual content
- `embedding`: 384-dimensional vector
- `metadata`:
  - `document_id`: Base document ID
  - `section`: Section type
  - `date`: Analysis date

### Performance Considerations
- Query time: ~1-2 seconds for 3 results per topic
- Storage: ~1GB per 100,000 documents
- Embedding generation: ~1-2 seconds per document

## Troubleshooting

### Common Issues

1. **No historical results found**
   - Run `populate_chromadb.py` to populate the database
   - Check that strategy analyses exist in `strategy_analyses/` directory

2. **ChromaDB errors**
   - Ensure ChromaDB is installed: `pip install chromadb==0.5.23`
   - Check write permissions for `./strategy_db_chroma` directory

3. **Memory errors**
   - Monitor disk space for ChromaDB storage
   - Consider implementing cleanup for old analyses

## Example Output

### Historical Context in Analysis
```
Based on our June 8 assessment, we predicted increased Chinese 
naval activity in the South China Sea. Current reports confirm 
this pattern, with 3 new artificial island constructions...

This matches the escalation pattern we identified in our May 28 
analysis, where we noted that economic pressures often precede 
military posturing...
```

### Learning Section
```
## LEARNING FROM PAST ASSESSMENTS

**Patterns Confirmed:**
- Chinese "gray zone" operations continue as predicted (June 3)
- Russian energy leverage remains primary tool (May 28)
- Middle East proxy dynamics unchanged (June 5)

**Predictions Validated:**
- ✓ NATO expansion discussions (predicted June 8, confirmed today)
- ✓ Cyber attacks on infrastructure (warned June 3, occurred June 10)

**Emerging Trends vs Historical Baseline:**
- Acceleration of AI military integration (2x faster than projected)
- New coalition patterns not seen in previous analyses
```

## Contributing

To improve the memory architecture:
1. Enhance chunking strategies in `db_manager.py`
2. Add new query topics in `run_gpse_improved_with_memory.py`
3. Implement visualization tools for historical patterns
4. Develop prediction tracking mechanisms

## Contact

For questions or issues with the memory architecture, consult the Memory Bank documentation in `/memory-bank/`.
