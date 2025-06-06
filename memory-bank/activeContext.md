# Active Context

## Current Status: LLM Model Configuration Updated (June 6, 2025)

### Latest Work - Agent-Specific LLM Configuration
Successfully updated the GPSE system to use different LLM models for each agent:

1. **Model Assignments**:
   - **News Scout**: Gemini 2.0 Flash Experimental (`gemini-2.0-flash-exp`)
   - **Geopolitical Analyst**: GPT-4o (OpenAI's latest reasoning model)
   - **Communicator/Archivist**: GPT-4o Mini

2. **Key Changes Made**:
   - Added `langchain-google-genai>=1.0.0` to requirements.txt
   - Updated `.env.example` to include `GOOGLE_API_KEY`
   - Modified `main_crew.py`:
     - Imported `ChatOpenAI` and `ChatGoogleGenerativeAI` from LangChain
     - Created `_initialize_llms()` method to instantiate specific LLMs
     - Updated each agent to use `llm` parameter instead of `llm_config`
     - Each agent now uses its designated model

3. **Technical Implementation**:
   - News Scout uses Google's Gemini API for fast, efficient news processing
   - Geopolitical Analyst uses OpenAI's GPT-4o for deep reasoning capabilities
   - Communicator uses GPT-4o Mini for cost-effective document generation

### Previous Work - Communicator/Master Archivist Prompt Update
Successfully updated the communicator prompt in config/agents.yaml with two new protocols:

1. **New Protocols Added**:
   - **STRATEGIC CONTINUITY TRACKING PROTOCOL**: 
     - Extracts actor identity and domains across assessments
     - Compares forecasted intent, posture, and trajectory to prior assessments
     - Tags sharp deviations with "Continuity Break – Actor: X"
     - Stores structured deltas for analyst retrieval
   - **EXPECTED FOLLOW-ON TRACKER**:
     - Captures and tags predicted actions with timeframes
     - Scans subsequent 3-5 documents for confirmation or silence
     - Flags absent developments as "Absent Follow-On – [description]"
     - Archives absences as structured signals without speculation

2. **Key Improvements**:
   - Enhanced continuity tracking across strategic assessments
   - Systematic monitoring of predicted developments
   - Better archival of strategic deviations and absences
   - Improved institutional memory capabilities

### Previous Work - News Scout Prompt Update
Successfully updated the news_scout prompt in config/agents.yaml with three new micro-protocols:

1. **New Micro-Protocols Added**:
   - **TEMPORAL ANOMALY MICRO-PROTOCOL**: Identifies reporting delays, early coverage coinciding with unrelated events, retractions/contradictions, and gaps between event occurrence and confirmation
   - **FRICTION TAGGING PROTOCOL**: Tags early-stage strategic friction across three dimensions:
     - Narrative Friction: Conflicting official/non-state descriptions
     - Infrastructure Friction: Unexplained critical system disruptions
     - Enforcement Friction: Sudden border/legal/cyber enforcement changes
   - **ACTOR EVENT CONTINUITY TRACKER**: Maintains 72-hour rolling log tracking repeated actions, unexpected silences, and tempo changes

2. **Key Improvements**:
   - Enhanced temporal awareness for identifying information operations
   - Systematic tagging of early warning signals
   - Better continuity tracking across multiple actor domains
   - More precise documentation of timing anomalies

### Previous Work - Geopolitical Analyst Prompt Update
Successfully updated the geo_analyst prompt in config/agents.yaml with enhanced analytical protocols:

1. **New Micro-Protocols Added**:
   - **RGT (Relational Game Theory) Micro-Protocol**: Models cascading effects through dependency loops, enforcement capabilities, and systemic instability points
   - **Creative Inference Micro-Protocol**: Systematically identifies absences, timing synchronicities, and causal forks
   - **Pretext & Counterfactual Micro-Protocol**: Identifies narrative prerequisites for escalatory moves
   - **Adversarial Stress Simulation**: Inverts comfortable assumptions to identify blind spots

2. **Enhanced Mandatory Output Sections**:
   - Added `[Pretextual Indicators]` - Signs of narrative/legal groundwork
   - Added `[Counterfactual Watch]` - Alternate interpretations with evidence
   - Added `[Blind Spot Stress Test]` - High-risk, low-visibility scenarios
   - Maintained all existing sections with enhanced clarity

3. **Key Improvements**:
   - More structured approach to creative inference
   - Systematic methods for identifying hidden preparations
   - Better framework for counterfactual analysis
   - Enhanced ability to identify strategic blind spots

### Previous Work (June 6, 2025 - Open Output File Button)
Successfully added "Open Output File" functionality to the GPSE GUI Runner:

1. **New Features in run_gpse_gui.py**:
   - Added `import platform` for cross-platform file opening support
   - Added `page.output_file_path` attribute to store the generated file path
   - Created `open_generated_file()` function that:
     - Retrieves stored file path from `page.output_file_path`
     - Detects the operating system (Windows/macOS/Linux)
     - Opens file using appropriate system command
     - Shows error if file doesn't exist
   - Modified `update_ui_with_result()` to:
     - Extract file path from success message
     - Store path in `page.output_file_path`
     - Enable the "Open Output File" button
   - Added new `open_file_button`:
     - Label: "Open Output File"
     - Width: 300px (matching run button)
     - Initially disabled
     - Enables after successful analysis
     - Opens generated markdown file in default application

2. **Cross-Platform Support**:
   - Windows: Uses `os.startfile()`
   - macOS: Uses `subprocess.call(['open', file_path])`
   - Linux: Uses `subprocess.call(['xdg-open', file_path])`

### Previous Work (June 5, 2025 - Threading Update)
Successfully modified the GPSE GUI Runner to use threading for non-blocking UI:

1. **Threading Implementation in run_gpse_gui.py**:
   - Added `import threading` module
   - Created `execute_crew_in_thread()` worker function that runs subprocess and returns status message
   - Created `update_ui_with_result()` function for thread-safe UI updates
   - Modified `start_gpse_analysis()` to use threading:
     - Creates thread with `thread_target_wrapper` 
     - Uses `page.run_thread_safe()` for UI updates from thread
     - UI remains responsive during long-running analysis

2. **Key Benefits**:
   - UI no longer freezes during subprocess execution
   - Status updates display immediately
   - Button properly disabled/enabled during processing
   - Clean separation of subprocess logic in worker function

### Previous Work (June 5, 2025 - GUI Creation)
Successfully created and tested the GPSE GUI Runner with Flet:

1. **Created Flet GUI Application (run_gpse_gui.py)**:
   - Simple, clean interface with welcome text
   - "Run GPSE Analysis" button (300px wide)
   - Status display showing current state
   - Window size: 700x500 pixels

2. **Key Features Implemented**:
   - Button disabling during processing to prevent multiple runs
   - Real-time status updates
   - UTF-8 encoding with error handling
   - No timeout (allows long-running analyses)
   - Selectable text for copying file paths
   - Proper error handling and display

3. **Fixed Issues**:
   - Resolved `output_filepath` AttributeError in main_crew.py
   - Removed emoji characters that caused encoding issues
   - Fixed pysqlite3-binary import (made optional)

4. **Successful Test**:
   - GUI ran GPSE analysis successfully
   - Created output file: `GGSM-June 05, 2025-DailyAnalysis.md`
   - Displayed absolute path: `C:\Users\every\Desktop\GPSE_Project\strategy_analyses\GGSM-June 05, 2025-DailyAnalysis.md`

### System Integration
- **main_crew.py**: Modified to use agent-specific LLM models
- **run_gpse_gui.py**: Captures and displays this path in the GUI (now with threading and file opening)
- **Flet GUI**: Provides user-friendly, non-blocking interface with file opening capability
- **config/agents.yaml**: All three agents enhanced with advanced micro-protocols

### Previous Work (June 3, 2025)
Successfully created comprehensive GitHub documentation for the GPSE project:

1. **Created Main Documentation**:
   - Updated README.md with clear instructions, architecture overview, and links
   - Created .env.example for easy API key setup
   - Added link to sample output documentation

2. **Created Detailed Guides**:
   - docs/SETUP_GUIDE.md - Step-by-step installation with troubleshooting
   - docs/SAMPLE_OUTPUT.md - Full example of a GPSE analysis
   - docs/ARCHITECTURE.md - Complete system design documentation

3. **Created Visual Diagrams** (Mermaid format):
   - docs/diagrams/system_architecture.mermaid - Overall system flow
   - docs/diagrams/data_flow.mermaid - Data pipeline visualization
   - docs/diagrams/agent_tools_mapping.mermaid - Agent-tool relationships

### System State
- **Working Version**: main_crew.py (with all Windows fixes + GUI support + agent-specific LLMs)
- **GUI Runner**: run_gpse_gui.py (Flet-based desktop application with threading + file opening)
- **Tools**: gpse_tools_comprehensive.py
- **Memory**: ChromaDB with Windows fixes implemented
- **Output**: Daily analyses saved to strategy_analyses/
- **GUI Support**: Absolute file path printed as last line of output
- **Threading**: GUI remains responsive during analysis execution
- **File Opening**: Cross-platform support for opening generated files
- **Agent Enhancements**: ALL agents now with advanced micro-protocols
- **LLM Configuration**: Each agent uses its own optimized model

### Key Features Working
- ✅ ChromaDB memory on Windows
- ✅ Multi-agent CrewAI system
- ✅ News aggregation from multiple sources
- ✅ Strategic analysis with frameworks
- ✅ Professional markdown output
- ✅ Historical context retention
- ✅ GUI integration support (absolute path output)
- ✅ Flet GUI runner application
- ✅ Non-blocking UI with threading
- ✅ Open Output File button with cross-platform support
- ✅ Enhanced news gathering with temporal anomaly detection
- ✅ Enhanced geopolitical analysis with counterfactual modeling
- ✅ Enhanced archival with continuity tracking and follow-on monitoring
- ✅ Agent-specific LLM models (Gemini for News Scout, GPT-4o for Analyst, GPT-4o Mini for Communicator)

### Documentation Structure
```
GPSE_Project/
├── README.md (main entry point)
├── .env.example (API key template - now includes GOOGLE_API_KEY)
├── main_crew.py (main script - GUI compatible with agent-specific LLMs)
├── run_gpse_gui.py (Flet GUI runner with threading + file opening)
├── config/
│   ├── agents.yaml (ALL agents enhanced with micro-protocols)
│   └── tasks_simplified.yaml
├── test_output_path.py (test helper)
├── docs/
│   ├── SETUP_GUIDE.md
│   ├── SAMPLE_OUTPUT.md
│   ├── ARCHITECTURE.md
│   └── diagrams/
│       ├── system_architecture.mermaid
│       ├── data_flow.mermaid
│       └── agent_tools_mapping.mermaid
└── strategy_analyses/ (output folder)
