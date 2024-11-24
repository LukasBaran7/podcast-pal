"""Tests for cache functionality"""
import pytest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import mock_open, patch

from podcast_pal.storage.cache import (
    load_cached_opml, 
    force_read_cache,
    is_cache_expired,
    get_cache_age,
    cache_opml,
    CACHE_MAX_AGE_HOURS
)
from podcast_pal.core.exceptions import StorageError

@pytest.fixture
def mock_cache_file():
    """Create a temporary cache file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write("cached opml data")
        temp_file.flush()
        yield temp_file.name
    os.unlink(temp_file.name)

def test_load_cached_opml_exists(mock_cache_file):
    """Test loading cached OPML when file exists and is not expired"""
    with patch('podcast_pal.storage.cache.CACHE_PATH', mock_cache_file):
        with patch('podcast_pal.storage.cache.is_cache_expired', return_value=False):
            result = load_cached_opml()
            assert result == "cached opml data"

def test_load_cached_opml_expired(mock_cache_file):
    """Test loading cached OPML when file is expired"""
    with patch('podcast_pal.storage.cache.CACHE_PATH', mock_cache_file):
        with patch('podcast_pal.storage.cache.is_cache_expired', return_value=True):
            result = load_cached_opml()
            assert result is None

def test_force_read_cache(mock_cache_file):
    """Test force reading cache regardless of expiration"""
    with patch('podcast_pal.storage.cache.CACHE_PATH', mock_cache_file):
        result = force_read_cache()
        assert result == "cached opml data"

def test_get_cache_age(mock_cache_file):
    """Test getting cache age information"""
    with patch('podcast_pal.storage.cache.CACHE_PATH', mock_cache_file):
        age = get_cache_age()
        assert isinstance(age, dict)
        assert all(key in age for key in ['hours', 'minutes', 'is_expired'])
        assert isinstance(age['hours'], int)
        assert isinstance(age['minutes'], int)
        assert isinstance(age['is_expired'], bool)

def test_cache_opml_success(mock_cache_file):
    """Test successful OPML caching"""
    with patch('podcast_pal.storage.cache.CACHE_PATH', mock_cache_file):
        cache_opml("new opml data")
        assert force_read_cache() == "new opml data"

def test_cache_opml_failure():
    """Test OPML caching failure"""
    with patch('builtins.open', mock_open()) as mock_file:
        mock_file.side_effect = IOError("Failed to write")
        with pytest.raises(StorageError):
            cache_opml("test data") 