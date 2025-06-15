import unittest
import datetime
from pydantic import ValidationError

from schemas import StrategicPathway, PathwayUpdate

class TestSchemas(unittest.TestCase):

    def test_pathway_update_valid(self):
        """Test successful creation of a PathwayUpdate object."""
        data = {
            "update_id": "update_123",
            "event_date": datetime.date.today(),
            "event_summary": "Test event summary.",
            "impact_analysis": "This event strengthens the pathway.",
            "impact_rating": "Strengthens"
        }
        try:
            PathwayUpdate.model_validate(data)
        except ValidationError as e:
            self.fail(f"PathwayUpdate validation failed unexpectedly: {e}")

    def test_pathway_update_invalid_rating(self):
        """Test that an invalid impact_rating raises a validation error."""
        data = {
            "update_id": "update_123",
            "event_date": datetime.date.today(),
            "event_summary": "Test event summary.",
            "impact_analysis": "This event has a weird impact.",
            "impact_rating": "Weird"
        }
        with self.assertRaises(ValidationError):
            PathwayUpdate.model_validate(data)

    def test_strategic_pathway_valid(self):
        """Test successful creation of a StrategicPathway object."""
        update_data = {
            "update_id": "update_456",
            "event_date": datetime.date.today(),
            "event_summary": "Initial event.",
            "impact_analysis": "This is the first event.",
            "impact_rating": "No Significant Impact"
        }
        pathway_data = {
            "pathway_id": "pathway_789",
            "source_analysis_id": "GGSM-20250615-TestAnalysis",
            "creation_date": datetime.date.today(),
            "last_updated": datetime.date.today(),
            "title": "Test Pathway",
            "description": "A test pathway for validation.",
            "key_actors": ["USA", "China"],
            "indicators": ["An indicator happens."],
            "status": "Emerging",
            "updates": [update_data]
        }
        try:
            StrategicPathway.model_validate(pathway_data)
        except ValidationError as e:
            self.fail(f"StrategicPathway validation failed unexpectedly: {e}")

    def test_strategic_pathway_invalid_status(self):
        """Test that an invalid status raises a validation error."""
        pathway_data = {
            "pathway_id": "pathway_789",
            "source_analysis_id": "GGSM-20250615-TestAnalysis",
            "creation_date": datetime.date.today(),
            "last_updated": datetime.date.today(),
            "title": "Test Pathway",
            "description": "A test pathway for validation.",
            "key_actors": ["USA", "China"],
            "indicators": ["An indicator happens."],
            "status": "InvalidStatus",
            "updates": []
        }
        with self.assertRaises(ValidationError):
            StrategicPathway.model_validate(pathway_data)

    def test_strategic_pathway_defaults(self):
        """Test that default values are set correctly."""
        pathway_data = {
            "pathway_id": "pathway_789",
            "source_analysis_id": "GGSM-20250615-TestAnalysis",
            "creation_date": datetime.date.today(),
            "last_updated": datetime.date.today(),
            "title": "Test Pathway",
            "description": "A test pathway for validation.",
            "key_actors": ["USA", "China"],
            "indicators": ["An indicator happens."],
            "status": "Active"
        }
        pathway = StrategicPathway.model_validate(pathway_data)
        self.assertEqual(pathway.updates, [])

if __name__ == '__main__':
    unittest.main()
