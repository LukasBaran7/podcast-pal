"""Tests for MongoDB storage functionality"""
import pytest
from unittest.mock import Mock, patch, ANY
from datetime import datetime

from podcast_pal.storage.mongodb import (
    get_mongodb_collection,
    update_podcast,
    _get_mongodb_config,
    _update_existing_podcast,
    _insert_new_podcast
)
from podcast_pal.core.exceptions import StorageError
from podcast_pal.core.podcast import Podcast, Episode

@pytest.fixture
def mock_episode():
    """Create a mock episode"""
    return Episode(
        title="Test Episode",
        audio_url="http://audio.url",
        overcast_url="http://overcast.url",
        overcast_id="ep123",
        published_date=datetime.now(),
        play_progress="50",
        last_played_at=datetime.now(),
        summary="Test summary"
    )

@pytest.fixture
def mock_podcast(mock_episode):
    """Create a mock podcast"""
    return Podcast(
        title="Test Podcast",
        artwork_url="http://artwork.url",
        episodes=[mock_episode],
        created_at=datetime.now(),
        source="overcast"
    )

@pytest.fixture
def mock_collection():
    """Create a mock MongoDB collection"""
    collection = Mock()
    collection.find_one.return_value = None
    collection.insert_one.return_value = Mock()
    collection.update_one.return_value = Mock()
    return collection

def test_get_mongodb_collection():
    """Test MongoDB collection initialization"""
    env_vars = {
        'PODCAST_DB': 'mongodb://localhost',
        'MONGODB_DATABASE': 'test_db',
        'MONGODB_COLLECTION': 'test_collection'
    }
    
    with patch.dict('os.environ', env_vars):
        with patch('podcast_pal.storage.mongodb.MongoClient') as mock_client:
            # Create mock objects
            mock_db = Mock()
            mock_collection = Mock()
            
            # Setup the chain of mocks
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance
            mock_client_instance.__getitem__ = Mock()
            mock_client_instance.__getitem__.return_value = mock_db
            mock_db.get_collection.return_value = mock_collection
            
            collection = get_mongodb_collection()
            
            assert collection == mock_collection
            mock_client.assert_called_once_with('mongodb://localhost')
            mock_client_instance.__getitem__.assert_called_once_with('test_db')
            mock_db.get_collection.assert_called_once_with('test_collection', codec_options=ANY)

def test_get_mongodb_config_missing_vars():
    """Test handling of missing environment variables"""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(StorageError) as exc_info:
            _get_mongodb_config()
        assert "Missing required environment variable" in str(exc_info.value)

def test_update_podcast_new(mock_collection, mock_podcast):
    """Test inserting a new podcast"""
    mock_collection.find_one.return_value = None
    
    result = update_podcast(mock_collection, mock_podcast)
    
    assert result is True
    mock_collection.insert_one.assert_called_once()
    # Verify the serialized data was passed
    args = mock_collection.insert_one.call_args[0][0]
    assert args["podcast_title"] == mock_podcast.title
    assert args["artwork_url"] == mock_podcast.artwork_url
    assert len(args["episodes"]) == len(mock_podcast.episodes)

def test_update_podcast_existing(mock_collection, mock_podcast):
    """Test updating an existing podcast"""
    existing_doc = {
        "_id": "123",
        "podcast_title": mock_podcast.title,
        "source": mock_podcast.source,  # Add source field
        "episodes": []
    }
    mock_collection.find_one.return_value = existing_doc
    
    result = update_podcast(mock_collection, mock_podcast)
    
    assert result is True
    mock_collection.update_one.assert_called_once()
    # Verify the serialized episodes were passed
    args = mock_collection.update_one.call_args[0][1]
    assert "$push" in args
    assert "episodes" in args["$push"]
    assert "$each" in args["$push"]["episodes"]

def test_update_podcast_no_new_episodes(mock_collection, mock_podcast):
    """Test updating podcast with no new episodes"""
    existing_doc = {
        "_id": "123",
        "podcast_title": mock_podcast.title,
        "episodes": [{"overcast_id": "ep123"}]  # Same ID as mock_episode
    }
    mock_collection.find_one.return_value = existing_doc
    
    result = update_podcast(mock_collection, mock_podcast)
    
    assert result is False
    mock_collection.update_one.assert_not_called()
    mock_collection.insert_one.assert_not_called()

def test_update_podcast_error(mock_collection, mock_podcast):
    """Test handling of MongoDB errors"""
    mock_collection.find_one.side_effect = Exception("Database error")
    
    with pytest.raises(StorageError) as exc_info:
        update_podcast(mock_collection, mock_podcast)
    assert "Failed to update podcast" in str(exc_info.value)

def test_update_existing_podcast(mock_collection, mock_podcast):
    """Test updating existing podcast with new episodes"""
    existing_doc = {
        "_id": "123",
        "podcast_title": mock_podcast.title,
        "source": mock_podcast.source,  # Add source field
        "episodes": []
    }
    
    result = _update_existing_podcast(mock_collection, existing_doc, mock_podcast)
    
    assert result is True
    mock_collection.update_one.assert_called_once()
    # Verify the update operation structure
    update_operation = mock_collection.update_one.call_args[0][1]
    assert "$push" in update_operation
    assert "episodes" in update_operation["$push"]
    assert "$each" in update_operation["$push"]["episodes"]
    serialized_episodes = update_operation["$push"]["episodes"]["$each"]
    assert len(serialized_episodes) == len(mock_podcast.episodes)

def test_insert_new_podcast(mock_collection, mock_podcast):
    """Test inserting a new podcast"""
    result = _insert_new_podcast(mock_collection, mock_podcast)
    
    assert result is True
    mock_collection.insert_one.assert_called_once()
    
    # Verify the serialized data structure
    called_arg = mock_collection.insert_one.call_args[0][0]
    assert called_arg["podcast_title"] == mock_podcast.title
    assert called_arg["artwork_url"] == mock_podcast.artwork_url
    assert called_arg["source"] == mock_podcast.source
    assert called_arg["created_at"] == mock_podcast.created_at
    assert len(called_arg["episodes"]) == len(mock_podcast.episodes)
    
    # Verify episode serialization
    episode = called_arg["episodes"][0]
    assert episode["title"] == mock_podcast.episodes[0].title
    assert episode["audio_url"] == mock_podcast.episodes[0].audio_url
    assert episode["overcast_id"] == mock_podcast.episodes[0].overcast_id