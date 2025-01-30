"""Tests for podcast processing functionality"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from xml.etree.ElementTree import Element
from dateutil.tz import gettz

from podcast_pal.processor import (
    process_podcasts,
    process_podcast,
    process_episode,
    should_process_played_episode,
    DAYS_TO_KEEP
)
from podcast_pal.core.podcast import Podcast, Episode

@pytest.fixture
def mock_raw_episode():
    """Create a mock episode XML element"""
    warsaw_tz = gettz('Europe/Warsaw')
    current_time = datetime.now(warsaw_tz)
    recent_time = current_time - timedelta(hours=1)  # Just 1 hour ago
    
    episode = Element('outline')
    episode.attrib.update({
        'title': 'Test Episode',
        'url': 'http://audio.url',
        'overcastUrl': 'http://overcast.url',
        'overcastId': 'ep123',
        'pubDate': current_time.isoformat(),
        'progress': '50',
        'userUpdatedDate': recent_time.isoformat(),  # Recent update time
        'played': '1'
    })
    return episode

@pytest.fixture
def mock_unplayed_episode(mock_raw_episode):
    """Create a mock unplayed episode"""
    # Create a new Element instead of modifying the existing one
    episode = Element('outline')
    episode.attrib.update(mock_raw_episode.attrib)  # Copy all attributes
    episode.attrib['played'] = '0'  # Set as unplayed
    return episode

@pytest.fixture
def mock_raw_podcast(mock_raw_episode, mock_unplayed_episode):
    """Create a mock podcast XML element with both played and unplayed episodes"""
    podcast = Element('outline')
    podcast.attrib['title'] = 'Test Podcast'
    podcast.append(mock_raw_episode)  # Add played episode
    podcast.append(mock_unplayed_episode)  # Add unplayed episode
    return podcast

@pytest.fixture
def mock_session():
    """Create a mock session"""
    return Mock()

def test_process_podcasts(mock_raw_podcast, mock_session):
    """Test processing multiple podcasts"""
    with patch('podcast_pal.processor.get_artwork_url', return_value='http://artwork.url'):
        with patch('podcast_pal.processor.get_episode_summary', return_value='Test summary'):
            played_podcasts, unplayed_podcasts = process_podcasts([mock_raw_podcast], mock_session)
            
            # Check played podcasts
            assert len(played_podcasts) == 1
            assert isinstance(played_podcasts[0], Podcast)
            assert played_podcasts[0].artwork_url == 'http://artwork.url'
            assert len(played_podcasts[0].episodes) == 1
            
            # Check unplayed podcasts
            assert len(unplayed_podcasts) == 1
            assert isinstance(unplayed_podcasts[0], Podcast)
            assert unplayed_podcasts[0].artwork_url == 'http://artwork.url'
            assert len(unplayed_podcasts[0].episodes) == 1

def test_process_podcast(mock_raw_podcast, mock_session):
    """Test processing a single podcast"""
    now = datetime.now().astimezone()
    
    with patch('podcast_pal.processor.get_artwork_url', return_value='http://artwork.url'):
        with patch('podcast_pal.processor.get_episode_summary', return_value='Test summary'):
            played_podcast, unplayed_podcast = process_podcast(mock_raw_podcast, now, mock_session)
            
            # Check played podcast
            assert isinstance(played_podcast, Podcast)
            assert played_podcast.title == 'Test Podcast'
            assert played_podcast.artwork_url == 'http://artwork.url'
            assert len(played_podcast.episodes) == 1
            
            # Check unplayed podcast
            assert isinstance(unplayed_podcast, Podcast)
            assert unplayed_podcast.title == 'Test Podcast'
            assert unplayed_podcast.artwork_url == 'http://artwork.url'
            assert len(unplayed_podcast.episodes) == 1

def test_process_episode(mock_raw_episode, mock_session):
    """Test processing a single episode"""
    with patch('podcast_pal.processor.get_episode_summary', return_value='Test summary'):
        episode = process_episode(mock_raw_episode, mock_session)
        
        assert isinstance(episode, Episode)
        assert episode.title == 'Test Episode'
        assert episode.audio_url == 'http://audio.url'
        assert episode.summary == 'Test summary'

def test_should_process_played_episode_recent(mock_raw_episode):
    """Test that recent played episodes should be processed"""
    warsaw_tz = gettz('Europe/Warsaw')
    now = datetime.now(warsaw_tz)
    
    # Ensure the episode's update time is very recent
    recent_time = now - timedelta(minutes=30)  # Just 30 minutes ago
    mock_raw_episode.attrib['userUpdatedDate'] = recent_time.isoformat()
    
    assert should_process_played_episode(mock_raw_episode, now) is True

def test_should_process_played_episode_old(mock_raw_episode):
    """Test that old played episodes should not be processed"""
    warsaw_tz = gettz('Europe/Warsaw')
    now = datetime.now(warsaw_tz)
    old_time = now - timedelta(days=DAYS_TO_KEEP + 1)
    mock_raw_episode.attrib['userUpdatedDate'] = old_time.isoformat()
    
    assert should_process_played_episode(mock_raw_episode, now) is False 