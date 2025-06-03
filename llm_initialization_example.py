"""
Example of how to properly initialize LLM objects in main_crew.py
This shows how to use environment variables and create LLM instances
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Step 1: Load environment variables from .env file
load_dotenv()

# Step 2: Get API keys from environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

# Step 3: Initialize OpenAI LLMs
# For GPT-3.5 Turbo (cheaper, faster, good for simple tasks)
gpt_3_5_turbo = ChatOpenAI(
    model="gpt-3.5-turbo",
    api_key=openai_api_key,
    temperature=0.7,  # Adjust for creativity (0=deterministic, 1=creative)
    max_tokens=2000   # Maximum response length
)

# For GPT-4 Turbo (more expensive, better reasoning, complex tasks)
gpt_4_turbo = ChatOpenAI(
    model="gpt-4-turbo-preview",  # or "gpt-4-0125-preview" for specific version
    api_key=openai_api_key,
    temperature=0.7,
    max_tokens=4000
)

# Step 4: Initialize Anthropic LLMs
# For Claude 4 Opus (newest, most capable model)
claude_4_opus = ChatAnthropic(
    model="claude-4-opus",  # The new Claude 4 Opus model
    api_key=anthropic_api_key,
    temperature=0.7,
    max_tokens=4000
)

# For Claude 3 Haiku (fast, cheaper)
claude_3_haiku = ChatAnthropic(
    model="claude-3-haiku-20240307",
    api_key=anthropic_api_key,
    temperature=0.7,
    max_tokens=2000
)

# Example: How to update the GPSECrew __init__ method
class GPSECrew:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get API keys
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Get LLM provider preference from environment
        self.llm_provider = os.getenv('LLM_PROVIDER', 'openai')
        
        # Initialize LLM objects based on provider
        if self.llm_provider == 'anthropic' and self.anthropic_api_key:
            # Use Anthropic models
            self.analyst_llm = ChatAnthropic(
                model="claude-4-opus",  # The new Claude 4 Opus
                api_key=self.anthropic_api_key,
                temperature=0.7,
                max_tokens=4000
            )
            self.support_llm = ChatAnthropic(
                model="claude-3-haiku-20240307",
                api_key=self.anthropic_api_key,
                temperature=0.7,
                max_tokens=2000
            )
        else:
            # Use OpenAI models (default)
            self.analyst_llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                api_key=self.openai_api_key,
                temperature=0.7,
                max_tokens=4000
            )
            self.support_llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                api_key=self.openai_api_key,
                temperature=0.7,
                max_tokens=2000
            )
    
    def create_agents(self):
        """Create agents using the initialized LLM objects."""
        # Information Curation Specialist
        info_curator = Agent(
            role='Information Curation Specialist',
            goal='Gather and synthesize recent global political news',
            backstory='You are an expert information analyst...',
            verbose=True,
            allow_delegation=False,
            tools=[self.news_search_tool, self.web_scraper_tool],
            llm=self.support_llm  # Use the initialized LLM object
        )
        
        # Lead Strategy Analyst
        strategy_analyst = Agent(
            role='Lead Strategy Analyst',
            goal='Produce comprehensive strategic analyses',
            backstory='You are a senior geopolitical strategist...',
            verbose=True,
            allow_delegation=False,
            tools=[self.db_query_tool],
            llm=self.analyst_llm  # Use the more powerful LLM
        )
        
        # Communications & Archival Lead
        comms_archival = Agent(
            role='Communications & Archival Lead',
            goal='Format analyses into standardized documents',
            backstory='You are responsible for transforming analyses...',
            verbose=True,
            allow_delegation=False,
            tools=[self.db_update_tool],
            llm=self.support_llm  # Use the support LLM
        )
        
        return {
            'info_curator': info_curator,
            'strategy_analyst': strategy_analyst,
            'comms_archival': comms_archival
        }


# Example of testing which model you're using
if __name__ == "__main__":
    load_dotenv()
    
    print("Environment Variables:")
    print(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    print(f"ANTHROPIC_API_KEY: {'Set' if os.getenv('ANTHROPIC_API_KEY') else 'Not set'}")
    print(f"LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'openai (default)')}")
    
    # Example of initializing and testing
    if os.getenv('OPENAI_API_KEY'):
        test_llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=os.getenv('OPENAI_API_KEY'),
            temperature=0
        )
        print("\nTesting GPT-3.5-Turbo...")
        # You can test with: response = test_llm.invoke("Say hello")
    
    if os.getenv('ANTHROPIC_API_KEY'):
        test_llm = ChatAnthropic(
            model="claude-4-opus",
            api_key=os.getenv('ANTHROPIC_API_KEY'),
            temperature=0
        )
        print("\nTesting Claude 4 Opus...")
        # You can test with: response = test_llm.invoke("Say hello")
