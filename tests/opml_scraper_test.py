import pytest
import requests
from xml.etree import ElementTree
from unittest.mock import Mock

from opml_scraper import fetch_opml, parse_opml, _handle_failed_request

@pytest.fixture
def mock_session():
    session = Mock()
    response = Mock(spec=requests.Response)
    response.status_code = 200
    response.text = '''<?xml version="1.0" encoding="utf-8"?>
        <opml version="1.0">
            <body>
                <outline type="rss" text="Test Podcast 1"/>
                <outline type="rss" text="Test Podcast 2"/>
            </body>
        </opml>'''
    session.get.return_value = response
    return session

def test_fetch_opml_success(mock_session):
    """Test successful OPML fetch"""
    response = fetch_opml(mock_session)
    assert response.status_code == 200
    mock_session.get.assert_called_once_with('https://overcast.fm/account/export_opml/extended')

def test_fetch_opml_failure(mock_session):
    """Test failed OPML fetch"""
    # Arrange
    mock_response = mock_session.get.return_value
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_response.headers = {"Content-Type": "text/plain"}

    # Act & Assert
    with pytest.raises(SystemExit) as exc_info:
        fetch_opml(mock_session)
    
    assert exc_info.value.code == 1
    mock_session.get.assert_called_once_with('https://overcast.fm/account/export_opml/extended')

def test_parse_opml(mock_session):
    """Test OPML parsing"""
    response = mock_session.get.return_value
    podcasts = parse_opml(response)
    assert len(podcasts) == 2
    assert all(podcast.get('type') == 'rss' for podcast in podcasts)
    # Should verify podcast attributes more thoroughly
    assert podcasts[0].get('text') == 'Test Podcast 1'
    assert podcasts[1].get('text') == 'Test Podcast 2'

def test_parse_opml_with_string():
    """Test OPML parsing with string input"""
    opml_string = '''<?xml version="1.0" encoding="utf-8"?>
        <opml version="1.0">
            <body>
                <outline type="rss" text="Test Podcast"/>
            </body>
        </opml>'''
    podcasts = parse_opml(opml_string)
    assert len(podcasts) == 1
    assert podcasts[0].get('type') == 'rss'
    assert podcasts[0].get('text') == 'Test Podcast'

