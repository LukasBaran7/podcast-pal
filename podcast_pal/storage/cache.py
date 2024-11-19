"""Cache management for podcast data"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional
from ..core.exceptions import StorageError

logger = logging.getLogger(__name__)

CACHE_PATH = '/tmp/overcast.opml'
CACHE_MAX_AGE_HOURS = 8

def is_cache_expired() -> bool:
    """Check if cache file is older than max age"""
    if not os.path.exists(CACHE_PATH):
        logger.debug(f"Cache file not found at {CACHE_PATH}")
        return True
    file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(CACHE_PATH))
    is_expired = file_age > timedelta(hours=CACHE_MAX_AGE_HOURS)
    if is_expired:
        logger.debug(f"Cache at {CACHE_PATH} is expired (age: {file_age.total_seconds()/3600:.1f} hours)")
    return is_expired

def force_read_cache() -> Optional[str]:
    """Force read the cache file regardless of expiration"""
    if not os.path.exists(CACHE_PATH):
        logger.debug(f"Cannot force read cache: file not found at {CACHE_PATH}")
        return None
    return _read_cache_file()

def get_cache_age() -> Optional[dict]:
    """Get the age of cache file in hours and minutes"""
    if not os.path.exists(CACHE_PATH):
        logger.debug(f"Cannot get cache age: file not found at {CACHE_PATH}")
        return None
        
    file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(CACHE_PATH))
    hours = file_age.total_seconds() / 3600
    
    age_info = {
        'hours': int(hours),
        'minutes': int((hours % 1) * 60),
        'is_expired': file_age > timedelta(hours=CACHE_MAX_AGE_HOURS)
    }
    
    logger.debug(f"Cache age at {CACHE_PATH}: {age_info['hours']}h {age_info['minutes']}m")
    return age_info

def load_cached_opml() -> Optional[str]:
    """Load cached OPML file if it exists and is not expired"""
    if not os.path.exists(CACHE_PATH):
        logger.debug(f"Cannot load cache: file not found at {CACHE_PATH}")
        return None
    if is_cache_expired():
        logger.debug(f"Cannot load cache: file at {CACHE_PATH} is expired")
        return None
    logger.info(f"Loading valid cache from {CACHE_PATH}")
    return _read_cache_file()

def cache_opml(content: str) -> None:
    """Cache OPML content to file"""
    try:
        with open(CACHE_PATH, 'w') as f:
            f.write(content)
        logger.info(f"Successfully cached OPML file to {CACHE_PATH}")
    except IOError as e:
        error_msg = f"Failed to cache OPML to {CACHE_PATH}: {str(e)}"
        logger.error(error_msg)
        raise StorageError(error_msg)

def _read_cache_file() -> Optional[str]:
    """Read and return contents of cache file"""
    try:
        with open(CACHE_PATH, 'r') as f:
            content = f.read()
            logger.debug(f"Successfully read cache file from {CACHE_PATH}")
            return content
    except IOError as e:
        logger.error(f"Error reading cached OPML from {CACHE_PATH}: {e}")
        return None 