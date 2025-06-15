import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from crewai import Agent, Task
from langchain_openai import ChatOpenAI

from db_manager_enhanced import ChromaDBManager
from schemas import PathwayUpdate
import uuid
import json

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PathwayMonitor:
    def __init__(self):
        self.db_manager = ChromaDBManager()
        o3_api_key = os.getenv('OPENAI_API_KEY_O3')
        if not o3_api_key:
            logger.warning("OPENAI_API_KEY_O3 not found, falling back to gpt-4-turbo")
            self.llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.3)
        else:
            self.llm = ChatOpenAI(
                model="o3",
                temperature=1.0,
                max_completion_tokens=4096,
                openai_api_key=o3_api_key
            )

    def run_monitor(self, daily_events: List[Dict[str, Any]]):
        """
        Monitors daily events and updates relevant strategic pathways.

        Args:
            daily_events: A list of dictionaries, each representing a key event.
                          Each dict should have 'summary' and 'key_actors' keys.
        """
        print("\n=== RUNNING STRATEGIC PATHWAY MONITOR ===")
        for event in daily_events:
            event_summary = event.get("summary")
            key_actors = event.get("key_actors", [])
            
            if not event_summary:
                continue

            print(f"\nProcessing event: {event_summary[:80]}...")
            
            # Find relevant pathways
            relevant_pathways = self.db_manager.find_relevant_pathways(event_summary, key_actors)
            
            if not relevant_pathways:
                print("  No relevant pathways found for this event.")
                continue

            print(f"  Found {len(relevant_pathways)} relevant pathways. Analyzing impact...")

            for pathway in relevant_pathways:
                # Generate the update analysis using an LLM call
                update_analysis = self._generate_update_analysis(pathway, event_summary)
                
                if update_analysis:
                    # Create the PathwayUpdate object
                    pathway_update = PathwayUpdate(
                        update_id=f"update_{uuid.uuid4().hex[:8]}",
                        event_date=datetime.now().date(),
                        event_summary=event_summary,
                        impact_analysis=update_analysis.get("impact_analysis", ""),
                        impact_rating=update_analysis.get("impact_rating", "No Significant Impact")
                    )
                    
                    # Update the pathway in the database
                    self.db_manager.update_pathway(pathway.pathway_id, pathway_update)
                    print(f"    -> Updated pathway: {pathway.title}")

    def _generate_update_analysis(self, pathway, event_summary) -> Dict[str, Any]:
        """
        Uses an LLM to generate an impact analysis for a given pathway and event.
        """
        prompt = f"""
        Role: You are a geopolitical strategist.

        Context:
        - We are tracking a potential strategic pathway titled: "{pathway.title}".
        - Its core idea is: "{pathway.description}".
        - A new event has occurred: "{event_summary}".

        Task:
        Analyze the impact of this event on the strategic pathway. Your analysis must be concise and structured as a JSON object conforming to the PathwayUpdate schema.
        - In the `impact_analysis` field, explain *how* and *why* this event affects the pathway. Does it accelerate it, block it, make it more or less likely, or change its nature?
        - In the `impact_rating` field, choose the most appropriate descriptor from the allowed list: ["Significantly Strengthens", "Strengthens", "No Significant Impact", "Weakens", "Significantly Weakens", "Alters Trajectory"].

        Return ONLY the JSON object.
        """
        
        try:
            response = self.llm.invoke(prompt)
            # The response should be a JSON string, so we parse it.
            analysis_data = json.loads(response.content)
            return analysis_data
        except Exception as e:
            logger.error(f"Error generating update analysis: {e}")
            return None

# Example Usage
if __name__ == "__main__":
    # This is a conceptual example of how this agent would be run.
    # In a real scenario, the `daily_events` would be populated by another agent or process.
    
    # Sample daily events
    sample_daily_events = [
        {
            "summary": "The US announces a full ban on the sale of advanced semiconductor technology to China, including restrictions on third-party sales.",
            "key_actors": ["USA", "China"]
        },
        {
            "summary": "A new defense pact is signed between Russia and North Korea, promising mutual military assistance in the event of an attack.",
            "key_actors": ["Russia", "North Korea", "USA", "South Korea"]
        }
    ]
    
    monitor = PathwayMonitor()
    monitor.run_monitor(sample_daily_events)
    print("\nPathway Monitor run complete.")
