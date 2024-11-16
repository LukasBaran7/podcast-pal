"""Cache management for podcast data"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional
from ..core.exceptions import StorageError

logger = logging.getLogger(__name__)

CACHE_PATH = '/tmp/overcast.opml'
CACHE_MAX_AGE_HOURS = 36

def is_cache_expired() -> bool:
    """Check if cache file is older than max age"""
    if not os.path.exists(CACHE_PATH):
        return True
    file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(CACHE_PATH))
    return file_age > timedelta(hours=CACHE_MAX_AGE_HOURS)

def force_read_cache() -> Optional[str]:
    """Force read the cache file regardless of expiration"""
    if not os.path.exists(CACHE_PATH):
        return None
    return _read_cache_file()

def get_cache_age() -> Optional[dict]:
    """Get the age of cache file in hours and minutes"""
    if not os.path.exists(CACHE_PATH):
        return None
        
    file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(CACHE_PATH))
    hours = file_age.total_seconds() / 3600
    
    return {
        'hours': int(hours),
        'minutes': int((hours % 1) * 60),
        'is_expired': file_age > timedelta(hours=CACHE_MAX_AGE_HOURS)
    }

def load_cached_opml() -> Optional[str]:
    """Load cached OPML file if it exists and is not expired"""
    if not os.path.exists(CACHE_PATH) or is_cache_expired():
        return None
    return _read_cache_file()

def cache_opml(content: str) -> None:
    """Cache OPML content to file"""
    try:
        with open(CACHE_PATH, 'w') as f:
            f.write(content)
        logger.info("Successfully cached OPML file")
    except IOError as e:
        raise StorageError(f"Failed to cache OPML: {str(e)}")

def _read_cache_file() -> Optional[str]:
    """Read and return contents of cache file"""
    try:
        with open(CACHE_PATH, 'r') as f:
            return f.read()
    except IOError as e:
        logger.error(f"Error reading cached OPML: {e}")
        return None 