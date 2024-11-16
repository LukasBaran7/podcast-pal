import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

CACHE_PATH = '/tmp/overcast.opml'
CACHE_MAX_AGE_HOURS = 24

def _is_cache_expired(cache_path):
    """Check if cache file is older than max age"""
    file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_path))
    return file_age > timedelta(hours=CACHE_MAX_AGE_HOURS)

def _read_cache_file(cache_path):
    """Read and return contents of cache file"""
    try:
        with open(cache_path, 'r') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading cached OPML: {e}")
        return None

def load_cached_opml():
    """Load cached OPML file if it exists and is not expired"""
    if not os.path.exists(CACHE_PATH):
        return None
        
    if _is_cache_expired(CACHE_PATH):
        logger.info(f"Cached OPML is older than {CACHE_MAX_AGE_HOURS} hour(s), will fetch fresh data")
        return None
        
    return _read_cache_file(CACHE_PATH)

def _write_cache_file(cache_path, content):
    """Write content to cache file"""
    try:
        with open(cache_path, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Unable to cache OPML file: {e}")
        return False

def cache_opml(response):
    """Cache the OPML response to a temporary file"""
    if _write_cache_file(CACHE_PATH, response.text):
        logger.info("Successfully cached OPML file")