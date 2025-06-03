# GPSE Setup Guide

This guide provides detailed instructions for setting up the Geopolitical Grand Strategy Engine (GPSE) on your system.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [API Key Configuration](#api-key-configuration)
4. [Windows-Specific Setup](#windows-specific-setup)
5. [Testing Your Installation](#testing-your-installation)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: Version 3.11 or higher
- **Memory**: At least 8GB RAM recommended
- **Storage**: 2GB free space for dependencies and data

### Required API Keys
You'll need to obtain the following API keys:

1. **OpenAI API Key** (Required)
   - Sign up at [platform.openai.com](https://platform.openai.com)
   - Generate an API key from your account settings
   - Ensure you have GPT-4 access (GPT-4o recommended)

2. **Tavily API Key** (Required)
   - Sign up at [tavily.com](https://tavily.com)
   - Free tier available with 1000 searches/month
   - Get your API key from the dashboard

3. **Serper API Key** (Optional)
   - Sign up at [serper.dev](https://serper.dev)
   - Provides additional search capabilities
   - Free tier available

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/GPSE_Project.git
cd GPSE_Project
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv gpse_venv

# Activate virtual environment
# Windows PowerShell:
.\gpse_venv\Scripts\Activate.ps1

# Windows Command Prompt:
gpse_venv\Scripts\activate.bat

# macOS/Linux:
source gpse_venv/bin/activate
```

You should see `(gpse_venv)` at the beginning of your command prompt.

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- CrewAI (multi-agent framework)
- ChromaDB (vector database)
- OpenAI (GPT-4 access)
- Tavily (news search)
- And other required packages

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your favorite text editor
# Windows: notepad .env
# macOS/Linux: nano .env
```

Add your API keys to the `.env` file:

```env
OPENAI_API_KEY=sk-your-openai-key-here
TAVILY_API_KEY=tvly-your-tavily-key-here
SERPER_API_KEY=your-serper-key-here  # Optional
```

## Windows-Specific Setup

### ChromaDB Configuration

GPSE includes automatic fixes for ChromaDB on Windows. These are already built into the main script, but here's what happens behind the scenes:

1. **Storage Path**: Automatically set to `C:\gpse_data` to avoid path length issues
2. **SQLite Fix**: Uses local segment manager to prevent file locking
3. **Temp Directory**: Configured for Windows compatibility

### PowerShell Execution Policy

If you get an execution policy error when activating the virtual environment:

```powershell
# Run PowerShell as Administrator and execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Testing Your Installation

### 1. Verify Dependencies

```bash
python -c "import crewai; print('CrewAI:', crewai.__version__)"
python -c "import chromadb; print('ChromaDB:', chromadb.__version__)"
python -c "import openai; print('OpenAI installed successfully')"
```

### 2. Test API Keys

```bash
# Test your OpenAI key
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OpenAI Key:', 'Configured' if os.getenv('OPENAI_API_KEY') else 'Missing')"

# Test your Tavily key
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Tavily Key:', 'Configured' if os.getenv('TAVILY_API_KEY') else 'Missing')"
```

### 3. Run a Test Analysis

```bash
python main_crew.py
```

The first run will:
- Initialize the ChromaDB database
- Fetch current news
- Generate a strategic analysis
- Save the output to `strategy_analyses/`

## Troubleshooting

### Common Issues

#### 1. "Module not found" Error
```bash
# Ensure virtual environment is activated
# You should see (gpse_venv) in your prompt

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. ChromaDB Permission Error (Windows)
```bash
# The script includes automatic fixes, but if issues persist:
# 1. Run PowerShell as Administrator
# 2. Execute: python main_crew.py
# 3. After first successful run, normal user mode should work
```

#### 3. API Key Errors
```bash
# Check your .env file exists and contains keys
cat .env  # Linux/macOS
type .env  # Windows

# Ensure no extra spaces or quotes around keys
# Correct: OPENAI_API_KEY=sk-abc123
# Wrong: OPENAI_API_KEY="sk-abc123"
```

#### 4. Rate Limiting
- Tavily free tier: 1000 searches/month
- OpenAI: Check your usage limits
- Solution: Wait or upgrade your plan

### Getting Help

If you encounter issues:

1. Check the [Windows ChromaDB Fix Guide](../WINDOWS_CHROMADB_FIX_GUIDE.md)
2. Review error messages carefully
3. Check your API key quotas
4. Open an issue on GitHub with:
   - Your operating system
   - Python version (`python --version`)
   - Error message
   - Steps to reproduce

## Next Steps

Once installation is complete:

1. **Run Daily Analysis**: `python main_crew.py`
2. **View Results**: Check `strategy_analyses/` folder
3. **Customize**: Modify agent prompts in the main script
4. **Contribute**: Submit improvements via pull requests

## Advanced Configuration

### Custom Storage Location

To use a different storage location (not recommended for Windows):

```python
# In main_crew.py, modify:
os.environ["CREWAI_STORAGE_DIR"] = r"Your\Custom\Path"
```

### Using Different AI Models

```env
# In .env file:
OPENAI_MODEL_NAME=gpt-4-turbo-preview  # Or other available models
```

### Proxy Configuration

If behind a corporate firewall:

```env
# In .env file:
HTTP_PROXY=http://your-proxy:port
HTTPS_PROXY=http://your-proxy:port
```

---

**Remember**: The virtual environment must be activated every time you run GPSE!
