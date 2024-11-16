import pytest
from datetime import datetime, timedelta
from dateutil.tz import gettz
from dateutil.parser import parse as parse_dt
from podcast_parser import should_process_episode

def test_should_process_episode_played_recent():
    """Test that recent played episodes should be processed"""
    warsaw_tz = gettz('Europe/Warsaw')
    now = datetime.now(warsaw_tz)
    recent_date = (now - timedelta(hours=12)).isoformat()
    
    episode = type('Episode', (), {'attrib': {
        'played': '1',
        'userUpdatedDate': recent_date
    }})()
    
    assert should_process_episode(episode, now) is True

def test_should_process_episode_played_old_configurable():
    """Test that old played episodes can be processed with custom days_to_keep"""
    warsaw_tz = gettz('Europe/Warsaw')
    now = datetime.now(warsaw_tz)
    old_date = (now - timedelta(days=2)).isoformat()
    
    episode = type('Episode', (), {'attrib': {
        'played': '1',
        'userUpdatedDate': old_date
    }})()
    
    # Should not process with default 1 day
    assert should_process_episode(episode, now) is False
    
    # Should process with 3 days setting
    assert should_process_episode(episode, now, days_to_keep=3) is True

def test_should_process_episode_unplayed():
    """Test that unplayed episodes should not be processed"""
    warsaw_tz = gettz('Europe/Warsaw')
    now = datetime.now(warsaw_tz)
    recent_date = (now - timedelta(hours=12)).isoformat()
    
    episode = type('Episode', (), {'attrib': {
        'played': '0',
        'userUpdatedDate': recent_date
    }})()
    
    assert should_process_episode(episode, now) is False
