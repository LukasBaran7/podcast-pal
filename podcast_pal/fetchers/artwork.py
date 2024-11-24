"""Artwork URL fetching functionality"""
import re
import logging
from typing import Optional
import requests
from ..core.exceptions import FetchError

logger = logging.getLogger(__name__)

def get_artwork_url(overcast_url: str, session: requests.Session) -> str:
    """Fetch the episode artwork URL from Overcast page"""
    content = _fetch_page_content(overcast_url, session)
    if not content:
        return ''
        
    artwork_pattern = 'img class="art fullart" src="(.*)"'
    matches = re.findall(artwork_pattern, content)
    
    if matches:
        return matches[0]
        
    logger.warning(f"Could not find artwork URL for {overcast_url}")
    return ''

def _fetch_page_content(url: str, session: requests.Session) -> Optional[str]:
    """Helper function to fetch page content"""
    try:
        return session.get(url).text
    except requests.RequestException as e:
        logger.error(f"Failed to fetch page content from {url}: {str(e)}")
        return None 