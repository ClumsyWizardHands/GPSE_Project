import os
import logging
from datetime import datetime, timedelta
from typing import List
from dotenv import load_dotenv
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
import json

from db_manager_enhanced import ChromaDBManager
from schemas import StrategicPathway

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeopoliticalCartographer:
    def __init__(self):
        self.db_manager = ChromaDBManager()
        o3_api_key = os.getenv('OPENAI_API_KEY_O3')
        if not o3_api_key:
            logger.warning("OPENAI_API_KEY_O3 not found, falling back to gpt-4-turbo")
            self.llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.5)
        else:
            self.llm = ChatOpenAI(
                model="o3",
                temperature=1.0,
                max_completion_tokens=4096,
                openai_api_key=o3_api_key
            )

    def generate_weekly_report(self) -> str:
        """
        Generates a weekly report synthesizing the evolution of strategic pathways.
        """
        print("\n=== GENERATING STRATEGIC LANDSCAPE REPORT ===")
        
        # 1. Retrieve all pathways from the database
        try:
            all_pathways_docs = self.db_manager.pathways_collection.get()
            all_pathways = [StrategicPathway.model_validate_json(doc) for doc in all_pathways_docs['documents']]
        except Exception as e:
            logger.error(f"Failed to retrieve pathways from database: {e}")
            return "Error: Could not retrieve strategic pathways from the database."

        if not all_pathways:
            return "No strategic pathways found in the database to analyze."

        # 2. Filter for pathways updated in the last 7 days
        one_week_ago = datetime.now().date() - timedelta(days=7)
        recent_pathways = [
            p for p in all_pathways if p.last_updated >= one_week_ago and p.updates
        ]

        if not recent_pathways:
            return f"# Strategic Landscape Report - {datetime.now().strftime('%Y-%m-%d')}\n\nNo significant pathway updates in the last 7 days."

        print(f"Found {len(recent_pathways)} pathways with recent updates.")

        # 3. Prepare the context for the LLM
        report_context = self._prepare_llm_context(recent_pathways, all_pathways)

        # 4. Generate the report using the LLM
        report = self._invoke_llm_for_report(report_context)
        
        # 5. Save the report to a file
        report_filename = f"strategy_analyses/Strategic_Landscape_Report-{datetime.now().strftime('%Y-%m-%d')}.md"
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Successfully saved weekly report to {report_filename}")
        except Exception as e:
            logger.error(f"Failed to save weekly report: {e}")

        return report

    def _prepare_llm_context(self, recent_pathways: List[StrategicPathway], all_pathways: List[StrategicPathway]) -> str:
        """Prepares the context string for the LLM prompt."""
        context_parts = ["# Analysis Context: Recently Updated Strategic Pathways\n"]
        for pathway in recent_pathways:
            context_parts.append(f"## Pathway: {pathway.title} (Status: {pathway.status})")
            context_parts.append(f"**Description:** {pathway.description}")
            context_parts.append("**Recent Updates:**")
            for update in pathway.updates[-3:]: # Show last 3 updates
                context_parts.append(
                    f"- **Event ({update.event_date})**: {update.event_summary}\n"
                    f"  - **Impact**: {update.impact_rating} - {update.impact_analysis}"
                )
            context_parts.append("\n---\n")
        
        context_parts.append("\n# Full List of All Tracked Pathways (for context on convergence/divergence)\n")
        for pathway in all_pathways:
             context_parts.append(f"- **{pathway.title}** (ID: {pathway.pathway_id}, Status: {pathway.status})")

        return "\n".join(context_parts)

    def _invoke_llm_for_report(self, context: str) -> str:
        """Invokes the LLM to generate the markdown report."""
        
        prompt = f"""
        Role: You are a Geopolitical Cartographer, a master strategist who looks at the entire board. You don't focus on single moves, but on the shifting patterns of power and potential. Your job is to zoom out and provide a weekly briefing on the changing map of what's possible.

        Context: You have been provided with a list of all strategic pathways that have been updated in the last 7 days, along with a full list of all tracked pathways for broader context.

        Task: Generate a markdown report (`Strategic_Landscape_Report-YYYY-MM-DD.md`) that answers the following questions:
        1.  **Top 3 Most Active Pathways:** Which pathways saw the most significant updates this week and why? What do these updates signify for the evolution of the pathway?
        2.  **Emerging Narratives:** Are there any new, significant pathways that were identified this week? (Note: This information is not in the context, so state if none were created or if you cannot determine this).
        3.  **Convergence & Divergence:** Are any previously separate pathways starting to interact or merge based on recent events? Are any pathways splitting into new, distinct possibilities? Use the full list of pathways to identify potential connections.
        4.  **Stalled Pathways:** Are there any important pathways (from the full list) that have seen no activity, and is that lack of activity itself significant? What might this imply?

        Your report should be a high-level synthesis, focusing on the strategic implications of these changes.

        {context}
        """
        
        print("Generating report with LLM...")
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error generating weekly report with LLM: {e}")
            return f"Error: Could not generate the report. Details: {e}"

# Example Usage
if __name__ == "__main__":
    cartographer = GeopoliticalCartographer()
    weekly_report = cartographer.generate_weekly_report()
    print("\n--- Generated Report ---")
    print(weekly_report)
