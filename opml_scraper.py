import requests
import sys
from xml.etree import ElementTree
import logging

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
        SystemExit: If the request fails
    """
    logger.info('Fetching latest OPML export from Overcast')
    response = session.get(OVERCAST_OPML_URL)
    
    if response.status_code != 200:
        _handle_failed_request(response)
    
    return response

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