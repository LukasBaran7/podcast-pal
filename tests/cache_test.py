import pytest
import os
from unittest.mock import mock_open, patch

from cache import cache_opml, load_cached_opml

@pytest.fixture
def mock_opml_data():
    return '''<?xml version="1.0" encoding="utf-8"?>
        <opml version="1.0">
            <body>
                <outline type="rss" text="Test Podcast"/>
            </body>
        </opml>'''

def test_cache_opml(mock_opml_data):
    """Test caching OPML data to file"""
    mock_file = mock_open()
    with patch('builtins.open', mock_file):
        mock_response = type('Response', (), {'text': mock_opml_data})()
        cache_opml(mock_response)
        
    mock_file.assert_called_once_with('/tmp/overcast.opml', 'w')
    mock_file().write.assert_called_once_with(mock_opml_data)

def test_load_cached_opml_exists():
    """Test loading cached OPML when file exists"""
    test_data = '<opml>test data</opml>'
    m = mock_open(read_data=test_data)
    with patch('builtins.open', m):
        with patch('os.path.exists', return_value=True):
            with patch('cache._is_cache_expired', return_value=False):
                result = load_cached_opml()
    
    assert result == test_data
    m.assert_called_once_with('/tmp/overcast.opml', 'r')

def test_load_cached_opml_not_exists():
    """Test loading cached OPML when file doesn't exist"""
    with patch('os.path.exists', return_value=False):
        result = load_cached_opml()
    
    assert result is None

def test_load_cached_opml_expired():
    """Test loading cached OPML when file is expired"""
    test_data = '<opml>test data</opml>'
    m = mock_open(read_data=test_data)
    with patch('builtins.open', m):
        with patch('os.path.exists', return_value=True):
            with patch('cache._is_cache_expired', return_value=True):
                result = load_cached_opml()
    
    assert result is None

def test_cache_opml_error():
    """Test caching OPML when write fails"""
    mock_file = mock_open()
    mock_file.side_effect = IOError("Write failed")
    with patch('builtins.open', mock_file):
        mock_response = type('Response', (), {'text': 'test data'})()
        cache_opml(mock_response)
        # Should log error but not raise exception
