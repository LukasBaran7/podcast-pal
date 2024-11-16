"""Tests for summary fetching functionality"""
import pytest
import requests
from unittest.mock import Mock, patch

from podcast_pal.fetchers.summary import get_episode_summary

@pytest.fixture
def mock_session():
    """Create a mock session"""
    session = Mock()
    session.get.return_value.text = '''
        <html>
            <meta name="og:description" content="Test episode summary">
        </html>
    '''
    return session

def test_get_summary_success(mock_session):
    """Test successful summary extraction"""
    summary = get_episode_summary(
        'http://overcast.fm/episode',
        'Default Title',
        mock_session
    )
    assert summary == 'Test episode summary'
    mock_session.get.assert_called_once_with('http://overcast.fm/episode')

def test_get_summary_not_found(mock_session):
    """Test when summary is not found"""
    mock_session.get.return_value.text = '<html>No summary here</html>'
    summary = get_episode_summary(
        'http://overcast.fm/episode',
        'Default Title',
        mock_session
    )
    assert summary == 'Default Title'

def test_get_summary_request_error(mock_session):
    """Test handling of request errors"""
    mock_session.get.side_effect = requests.RequestException()
    summary = get_episode_summary(
        'http://overcast.fm/episode',
        'Default Title',
        mock_session
    )
    assert summary == 'Default Title' 