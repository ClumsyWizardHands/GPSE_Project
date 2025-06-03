# 🌍 GPSE - Geopolitical Grand Strategy Engine

An AI-powered multi-agent system that provides daily strategic intelligence analysis of global geopolitical developments, focusing on great power dynamics between the United States, China, and Russia.

## 🎯 What is GPSE?

GPSE uses CrewAI's multi-agent framework to create a sophisticated intelligence analysis pipeline that:
- 📰 Gathers real-time news from multiple sources
- 🔍 Analyzes developments through strategic frameworks
- 📊 Produces professional intelligence briefs
- 💾 Maintains historical context with ChromaDB

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/GPSE_Project.git
cd GPSE_Project

# 2. Create virtual environment
python -m venv gpse_venv

# 3. Activate virtual environment (Windows)
.\gpse_venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure API keys (copy .env.example to .env and add your keys)
copy .env.example .env

# 6. Run GPSE
python main_crew.py
```

## 📋 Requirements

- Python 3.11+
- Windows 10/11 (Linux/Mac compatible with minor adjustments)
- API Keys:
  - OpenAI API Key (GPT-4 access recommended)
  - Tavily API Key (for news search)
  - Serper API Key (optional, for additional search)

## 🔧 Detailed Installation

### 1. Environment Setup

```bash
# Create and activate virtual environment
python -m venv gpse_venv

# Windows
.\gpse_venv\Scripts\Activate.ps1

# Linux/Mac
source gpse_venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
SERPER_API_KEY=your_serper_api_key_here (optional)
```

### 4. Windows-Specific Setup

For Windows users, GPSE includes automatic ChromaDB fixes. No additional configuration needed!

## 💻 Usage

### Daily Analysis

Run the main script:

```bash
python main_crew.py
```

The system will:
1. Gather news from the last 24-48 hours
2. Analyze developments through strategic frameworks
3. Generate a comprehensive intelligence brief
4. Save the analysis to `strategy_analyses/GGSM-[Date]-DailyAnalysis.md`

### Output Location

Your daily analyses are saved in:
```
strategy_analyses/
├── GGSM-June 03, 2025-DailyAnalysis.md
├── GGSM-June 02, 2025-DailyAnalysis.md
└── ...
```

## 🏗️ System Architecture

![System Architecture](docs/diagrams/system_architecture.png)

GPSE uses three specialized AI agents:

1. **📡 News Scout**: Gathers and filters geopolitical news
2. **🧠 Strategic Analyst**: Applies strategic frameworks and historical context
3. **📝 Communicator**: Produces clear, actionable intelligence briefs

## 📊 Sample Output

GPSE generates comprehensive strategic intelligence briefs with:
- Executive summaries
- Critical developments with source links
- Strategic assessments and risk analysis
- Actionable recommendations
- Scenario planning

[View Full Sample Output](docs/SAMPLE_OUTPUT.md)

## 🪟 Windows-Specific Notes

GPSE includes automatic fixes for ChromaDB on Windows:
- Handles path length limitations
- Resolves file locking issues
- Manages SQLite compatibility

If you encounter permission errors, see [WINDOWS_CHROMADB_FIX_GUIDE.md](WINDOWS_CHROMADB_FIX_GUIDE.md)

## 📁 Project Structure

```
GPSE_Project/
├── main_crew.py              # Main execution script
├── gpse_tools_comprehensive.py # Tool implementations
├── requirements.txt          # Python dependencies
├── .env.example             # API key template
├── config/
│   ├── agents.yaml          # Agent configurations
│   └── tasks.yaml           # Task templates
├── strategy_analyses/       # Output directory
├── memory-bank/            # Project documentation
└── docs/                   # Additional documentation
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📚 Documentation

- [Setup Guide](docs/SETUP_GUIDE.md) - Detailed installation instructions
- [Architecture](docs/ARCHITECTURE.md) - System design and data flow
- [Sample Output](docs/SAMPLE_OUTPUT.md) - Example analysis output
- [Windows Fix Guide](WINDOWS_CHROMADB_FIX_GUIDE.md) - ChromaDB troubleshooting

## 📈 Roadmap

- [ ] Web interface for easier access
- [ ] Additional news sources integration
- [ ] Custom analysis templates
- [ ] Historical trend visualization
- [ ] Email delivery of daily briefs

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [CrewAI](https://github.com/joaomdmoura/crewAI)
- Powered by OpenAI GPT-4
- News search by [Tavily](https://tavily.com)

---

**Created by**: [Your Name]  
**Contact**: [Your Email/GitHub]
