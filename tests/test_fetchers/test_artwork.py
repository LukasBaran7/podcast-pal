"""Tests for artwork fetching functionality"""
import pytest
import requests
from unittest.mock import Mock, patch

from podcast_pal.fetchers.artwork import get_artwork_url

@pytest.fixture
def mock_session():
    """Create a mock session"""
    session = Mock()
    session.get.return_value.text = '''
        <html>
            <img class="art fullart" src="http://artwork.url/image.jpg">
        </html>
    '''
    return session

def test_get_artwork_url_success(mock_session):
    """Test successful artwork URL extraction"""
    url = get_artwork_url('http://overcast.fm/episode', mock_session)
    assert url == 'http://artwork.url/image.jpg'
    mock_session.get.assert_called_once_with('http://overcast.fm/episode')

def test_get_artwork_url_not_found(mock_session):
    """Test when artwork URL is not found"""
    mock_session.get.return_value.text = '<html>No artwork here</html>'
    url = get_artwork_url('http://overcast.fm/episode', mock_session)
    assert url == ''

def test_get_artwork_url_request_error(mock_session):
    """Test handling of request errors"""
    mock_session.get.side_effect = requests.RequestException()
    url = get_artwork_url('http://overcast.fm/episode', mock_session)
    assert url == '' 