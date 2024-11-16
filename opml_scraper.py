import requests
import sys
from xml.etree import ElementTree
import logging
from cache import force_read_cache, _is_cache_expired, CACHE_PATH, CACHE_MAX_AGE_HOURS

logger = logging.getLogger(__name__)

OVERCAST_OPML_URL = 'https://overcast.fm/account/export_opml/extended'

def fetch_opml(session):
    """
    Fetch the latest detailed OPML export from Overcast.
    
    Args:
        session: Authenticated requests session
        
    Returns:
        requests.Response: Response containing OPML data
        
    Raises:
        requests.RequestException: If the request fails and no cache is available
    """
    logger.info('Fetching latest OPML export from Overcast')
    try:
        response = session.get(OVERCAST_OPML_URL)
        
        if response.status_code != 200:
            cached_data = force_read_cache()
            if cached_data:
                if _is_cache_expired(CACHE_PATH):
                    logger.warning(f'Using expired cache (older than {CACHE_MAX_AGE_HOURS} hours) due to API error')
                else:
                    logger.info('Using valid cache due to API error')
                return type('Response', (), {'text': cached_data})()
                
            if response.status_code == 429:
                logger.error('Rate limited by Overcast API and no cache available')
            _handle_failed_request(response)
        
        return response
        
    except requests.RequestException as e:
        logger.warning(f'Request failed: {str(e)}, attempting to use cache')
        cached_data = force_read_cache()
        if cached_data:
            if _is_cache_expired(CACHE_PATH):
                logger.warning(f'Using expired cache (older than {CACHE_MAX_AGE_HOURS} hours) due to API error')
            else:
                logger.info('Using valid cache due to API error')
            return type('Response', (), {'text': cached_data})()
        raise

def _handle_failed_request(response):
    """Log error details and exit on failed request"""
    logger.error('Failed to fetch OPML')
    logger.error(f'Response text: {response.text}')
    logger.error(f'Response headers: {response.headers}')
    sys.exit(1)  # Use exit code 1 to indicate error

def parse_opml(response):
    """
    Parse the OPML response and find all podcasts.
    
    Args:
        response: Either requests.Response object or string containing OPML
        
    Returns:
        list: XML elements representing podcasts
    """
    text = response.text if isinstance(response, requests.Response) else response
    tree = ElementTree.fromstring(text)
    return tree.findall(".//*[@type='rss']")