import unittest
from unittest.mock import MagicMock, patch, ANY
import datetime
import json

# Mock the schemas before importing the manager
from schemas import StrategicPathway, PathwayUpdate

class TestChromaDBManager(unittest.TestCase):

    @patch('db_manager_enhanced.chromadb.PersistentClient')
    @patch('db_manager_enhanced.SentenceTransformer')
    def setUp(self, mock_sentence_transformer, mock_persistent_client):
        """Set up a mock environment for the ChromaDBManager."""
        # Mock the SentenceTransformer model
        self.mock_model = MagicMock()
        self.mock_model.encode.return_value.tolist.return_value = [0.1] * 384
        mock_sentence_transformer.return_value = self.mock_model

        # Mock the ChromaDB client and collections
        self.mock_client = MagicMock()
        self.mock_grand_strategy_collection = MagicMock()
        self.mock_pathways_collection = MagicMock()
        
        # Configure the client to return the correct mock collection
        self.mock_client.get_or_create_collection.side_effect = [
            self.mock_grand_strategy_collection,
            self.mock_pathways_collection
        ]
        mock_persistent_client.return_value = self.mock_client

        # Now we can import and instantiate the manager
        from db_manager_enhanced import ChromaDBManager
        self.manager = ChromaDBManager(db_path='./test_db')
        # The __init__ will call get_or_create_collection twice, so we need to adjust the mock
        self.manager.collection = self.mock_grand_strategy_collection
        self.manager.pathways_collection = self.mock_pathways_collection


    def test_add_pathway(self):
        """Test adding a valid StrategicPathway to the database."""
        pathway = StrategicPathway(
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
        
        result = self.manager.add_pathway(pathway)
        
        self.assertTrue(result)
        self.mock_pathways_collection.add.assert_called_once()
        call_args = self.mock_pathways_collection.add.call_args[1]
        self.assertEqual(call_args['ids'], ["test_path_001"])
        self.assertIn("Test Pathway", call_args['documents'][0])

    def test_update_pathway(self):
        """Test updating an existing pathway."""
        pathway_id = "test_path_002"
        original_pathway = StrategicPathway(
            pathway_id=pathway_id,
            source_analysis_id="test_source_002",
            creation_date=datetime.date.today(),
            last_updated=datetime.date.today(),
            title="Original Pathway",
            description="An existing pathway.",
            key_actors=["Actor B"],
            indicators=["Indicator 2"],
            status="Active"
        )
        
        # Mock the 'get' method to return the original pathway
        self.mock_pathways_collection.get.return_value = {
            'documents': [original_pathway.model_dump_json()]
        }
        
        update_data = PathwayUpdate(
            update_id="update_001",
            event_date=datetime.date.today(),
            event_summary="A new event occurred.",
            impact_analysis="The event alters the trajectory.",
            impact_rating="Alters Trajectory"
        )
        
        result = self.manager.update_pathway(pathway_id, update_data)
        
        self.assertTrue(result)
        self.mock_pathways_collection.get.assert_called_with(ids=[pathway_id])
        self.mock_pathways_collection.upsert.assert_called_once()
        
        # Check that the upserted data contains the update
        upsert_args = self.mock_pathways_collection.upsert.call_args[1]
        updated_pathway_json = upsert_args['documents'][0]
        updated_pathway = StrategicPathway.model_validate_json(updated_pathway_json)
        
        self.assertEqual(len(updated_pathway.updates), 1)
        self.assertEqual(updated_pathway.updates[0].update_id, "update_001")

    def test_find_relevant_pathways(self):
        """Test finding relevant pathways based on an event."""
        pathway = StrategicPathway(
            pathway_id="test_path_003",
            source_analysis_id="test_source_003",
            creation_date=datetime.date.today(),
            last_updated=datetime.date.today(),
            title="Relevant Pathway",
            description="A pathway about semiconductors.",
            key_actors=["USA", "China"],
            indicators=["US restricts chip sales"],
            status="Active"
        )
        
        # Mock the query result
        self.mock_pathways_collection.query.return_value = {
            'documents': [[pathway.model_dump_json()]]
        }
        
        event_summary = "The United States has banned semiconductor sales to China."
        key_actors = ["USA", "China"]
        
        results = self.manager.find_relevant_pathways(event_summary, key_actors)
        
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], StrategicPathway)
        self.assertEqual(results[0].pathway_id, "test_path_003")
        self.mock_pathways_collection.query.assert_called_once()

if __name__ == '__main__':
    unittest.main()
