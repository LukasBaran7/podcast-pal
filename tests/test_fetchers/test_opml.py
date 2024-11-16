"""Tests for OPML fetching functionality"""
import pytest
import requests
from unittest.mock import Mock, patch

from podcast_pal.fetchers.opml import (
    fetch_opml,
    parse_opml,
    _handle_failed_response,
    OVERCAST_OPML_URL
)
from podcast_pal.core.exceptions import FetchError

@pytest.fixture
def mock_session():
    """Create a mock session with successful response"""
    session = Mock()
    response = Mock(spec=requests.Response)
    response.status_code = 200
    response.text = '''<?xml version="1.0" encoding="utf-8"?>
        <opml version="1.0">
            <body>
                <outline type="rss" title="Test Podcast 1"/>
                <outline type="rss" title="Test Podcast 2"/>
            </body>
        </opml>'''
    session.get.return_value = response
    return session

def test_fetch_opml_success(mock_session):
    """Test successful OPML fetch"""
    response = fetch_opml(mock_session)
    assert response.status_code == 200
    mock_session.get.assert_called_once_with(OVERCAST_OPML_URL)

def test_fetch_opml_uses_cache_on_error(mock_session):
    """Test fallback to cache on fetch error"""
    mock_session.get.return_value.status_code = 429
    cached_data = "cached opml content"
    
    with patch('podcast_pal.fetchers.opml.force_read_cache', return_value=cached_data):
        with patch('podcast_pal.fetchers.opml.is_cache_expired', return_value=False):
            response = fetch_opml(mock_session)
            assert response.text == cached_data

def test_fetch_opml_raises_error_no_cache(mock_session):
    """Test error when fetch fails and no cache exists"""
    mock_session.get.side_effect = requests.RequestException("Network error")
    
    with patch('podcast_pal.fetchers.opml.force_read_cache', return_value=None):
        with pytest.raises(FetchError):
            fetch_opml(mock_session)

def test_parse_opml_valid():
    """Test parsing valid OPML content"""
    content = '''<?xml version="1.0" encoding="utf-8"?>
        <opml version="1.0">
            <body>
                <outline type="rss" title="Test Podcast"/>
            </body>
        </opml>'''
    result = parse_opml(content)
    assert len(result) == 1
    assert result[0].attrib['title'] == "Test Podcast"

def test_parse_opml_invalid():
    """Test parsing invalid OPML content"""
    with pytest.raises(FetchError):
        parse_opml("invalid xml content") 