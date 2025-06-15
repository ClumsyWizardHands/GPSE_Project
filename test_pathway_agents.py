import unittest
from unittest.mock import MagicMock, patch
import datetime
import json

from schemas import StrategicPathway, PathwayUpdate

class TestPathwayAgents(unittest.TestCase):

    @patch('pathway_monitor_agent.ChromaDBManager')
    @patch('pathway_monitor_agent.ChatOpenAI')
    def test_pathway_monitor(self, mock_chat_openai, mock_chroma_db_manager):
        """Test the PathwayMonitor agent's logic."""
        from pathway_monitor_agent import PathwayMonitor

        # Setup mocks
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = json.dumps({
            "impact_analysis": "Mocked impact analysis.",
            "impact_rating": "Strengthens"
        })
        mock_chat_openai.return_value = mock_llm

        mock_db = MagicMock()
        mock_pathway = StrategicPathway(
            pathway_id="test_path_001",
            source_analysis_id="test_source_001",
            creation_date=datetime.date.today(),
            last_updated=datetime.date.today(),
            title="Test Pathway",
            description="A test pathway.",
            key_actors=["Actor A"],
            indicators=["Indicator 1"],
            status="Emerging"
        )
        mock_db.find_relevant_pathways.return_value = [mock_pathway]
        mock_chroma_db_manager.return_value = mock_db

        # Instantiate and run the monitor
        monitor = PathwayMonitor()
        sample_events = [{"summary": "An event happened", "key_actors": ["Actor A"]}]
        monitor.run_monitor(sample_events)

        # Assertions
        mock_db.find_relevant_pathways.assert_called_once_with("An event happened", ["Actor A"])
        mock_llm.invoke.assert_called_once()
        mock_db.update_pathway.assert_called_once()
        
        # Check the data passed to update_pathway
        call_args = mock_db.update_pathway.call_args[0]
        self.assertEqual(call_args[0], "test_path_001")
        self.assertIsInstance(call_args[1], PathwayUpdate)
        self.assertEqual(call_args[1].impact_rating, "Strengthens")

    @patch('cartographer_agent.ChromaDBManager')
    @patch('cartographer_agent.ChatOpenAI')
    def test_geopolitical_cartographer(self, mock_chat_openai, mock_chroma_db_manager):
        """Test the GeopoliticalCartographer agent's logic."""
        from cartographer_agent import GeopoliticalCartographer

        # Setup mocks
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = "# Weekly Report\n\nThis is a mock report."
        mock_chat_openai.return_value = mock_llm

        mock_db = MagicMock()
        mock_pathway = StrategicPathway(
            pathway_id="test_path_001",
            source_analysis_id="test_source_001",
            creation_date=datetime.date.today() - datetime.timedelta(days=10),
            last_updated=datetime.date.today() - datetime.timedelta(days=3),
            title="Test Pathway",
            description="A test pathway.",
            key_actors=["Actor A"],
            indicators=["Indicator 1"],
            status="Active",
            updates=[PathwayUpdate(
                update_id="update_1",
                event_date=datetime.date.today() - datetime.timedelta(days=3),
                event_summary="An event.",
                impact_analysis="An impact.",
                impact_rating="Strengthens"
            )]
        )
        mock_db.pathways_collection.get.return_value = {
            'documents': [mock_pathway.model_dump_json()]
        }
        mock_chroma_db_manager.return_value = mock_db

        # Instantiate and run the cartographer
        cartographer = GeopoliticalCartographer()
        report = cartographer.generate_weekly_report()

        # Assertions
        mock_db.pathways_collection.get.assert_called_once()
        mock_llm.invoke.assert_called_once()
        self.assertIn("# Weekly Report", report)
        
        # Check that the context passed to the LLM is correct
        llm_call_args = mock_llm.invoke.call_args[0]
        self.assertIn("Pathway: Test Pathway", llm_call_args[0])
        self.assertIn("Impact**: Strengthens - An impact.", llm_call_args[0])


if __name__ == '__main__':
    unittest.main()
