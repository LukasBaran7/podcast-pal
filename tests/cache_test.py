import pytest
import tempfile
import os
from unittest.mock import mock_open, patch
from cache import load_cached_opml, force_read_cache

def test_load_cached_opml_exists():
    """Test loading cached OPML when file exists"""
    mock_data = "cached opml data"
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write(mock_data)
        temp_file.flush()
        
        with patch('cache.CACHE_PATH', temp_file.name):
            result = load_cached_opml()
            
    os.unlink(temp_file.name)
    assert result == mock_data

def test_load_cached_opml_not_exists():
    """Test loading cached OPML when file doesn't exist"""
    with tempfile.NamedTemporaryFile() as temp_file:
        # Delete the temp file to simulate non-existent file
        temp_file_path = temp_file.name
    
    with patch('cache.CACHE_PATH', temp_file_path):
        result = load_cached_opml()
        
    assert result is None

def test_force_read_cache():
    """Test force reading cache regardless of existence"""
    mock_data = "forced cache data"
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write(mock_data)
        temp_file.flush()
        
        with patch('cache.CACHE_PATH', temp_file.name):
            result = force_read_cache()
            
    os.unlink(temp_file.name)
    assert result == mock_data
