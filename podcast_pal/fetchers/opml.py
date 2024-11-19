"""OPML fetching and parsing functionality"""
import logging
import requests
from xml.etree import ElementTree
from typing import List, Optional
from ..core.exceptions import FetchError
from ..core.podcast import RawPodcastData
from ..storage.cache import cache_opml, force_read_cache, is_cache_expired

logger = logging.getLogger(__name__)

OVERCAST_OPML_URL = 'https://overcast.fm/account/export_opml/extended'

def fetch_opml(session) -> requests.Response:
    """Fetch the latest detailed OPML export from Overcast"""
    logger.info('Fetching latest OPML export from Overcast')
    try:
        response = session.get(OVERCAST_OPML_URL)
        
        if response.status_code != 200:
            cached_data = _handle_failed_response(response)
            return _create_mock_response(cached_data)
        
        # Cache the response immediately after successful download
        cache_opml(response.text)
        return response
        
    except requests.RequestException as e:
        logger.warning(f'Request failed: {str(e)}, attempting to use cache')
        cached_data = force_read_cache()
        if cached_data:
            return _create_mock_response(cached_data)
        raise FetchError(f"Failed to fetch OPML: {str(e)}")

def parse_opml(content: str) -> List[RawPodcastData]:
    """Parse OPML content into podcast data"""
    try:
        tree = ElementTree.fromstring(content)
        return tree.findall(".//*[@type='rss']")
    except ElementTree.ParseError as e:
        raise FetchError(f"Failed to parse OPML: {str(e)}")

def _handle_failed_response(response: requests.Response) -> Optional[str]:
    """Handle failed API response and attempt to use cache"""
    cached_data = force_read_cache()
    if cached_data:
        if is_cache_expired():
            logger.warning('Using expired cache due to API error')
        else:
            logger.info('Using valid cache due to API error')
        return cached_data
            
    if response.status_code == 429:
        logger.error('Rate limited by Overcast API and no cache available')
    raise FetchError(f"Failed to fetch OPML: {response.status_code}")

def _create_mock_response(content: str) -> requests.Response:
    """Create a mock response object with cached content"""
    return type('Response', (), {'text': content})()