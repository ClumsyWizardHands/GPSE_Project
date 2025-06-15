from pydantic import BaseModel, Field
from typing import List, Literal
import datetime

class PathwayUpdate(BaseModel):
    update_id: str = Field(description="Unique ID for the update event.")
    event_date: datetime.date = Field(description="Date of the triggering event.")
    event_summary: str = Field(description="Brief summary of the real-world event.")
    impact_analysis: str = Field(description="Analysis of how the event impacts the pathway (strengthens, weakens, alters, etc.).")
    impact_rating: Literal["Significantly Strengthens", "Strengthens", "No Significant Impact", "Weakens", "Significantly Weakens", "Alters Trajectory"]

class StrategicPathway(BaseModel):
    pathway_id: str = Field(description="Unique ID for the pathway, e.g., 'pathway_20250615_001'.")
    source_analysis_id: str = Field(description="The GGSM-*.md file ID where this pathway was first identified.")
    creation_date: datetime.date = Field(description="Date the pathway was first identified.")
    last_updated: datetime.date = Field(description="Date of the last update.")
    
    title: str = Field(description="A short, descriptive title for the pathway.")
    description: str = Field(description="A detailed narrative of the strategic pathway, its key assumptions, and potential end-states.")
    key_actors: List[str] = Field(description="List of countries, organizations, or groups central to this pathway.")
    
    # Indicators are crucial for the monitoring agent
    indicators: List[str] = Field(description="A list of specific, observable events or metrics that would signal this pathway is evolving.")
    
    status: Literal["Emerging", "Active", "Stalled", "Converging", "Diverging", "Archived"] = Field(description="The current status of the pathway.")
    
    updates: List[PathwayUpdate] = Field(default=[], description="A chronological log of events and updates impacting this pathway.")
