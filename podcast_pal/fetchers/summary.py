"""Summary fetching functionality"""
import re
import logging
import requests
from typing import Optional
from ..core.exceptions import FetchError

logger = logging.getLogger(__name__)

def get_episode_summary(overcast_url: str, default_title: str, session: requests.Session) -> str:
    """
    Fetch the episode summary from Overcast page.
    
    Args:
        overcast_url: URL of the episode page
        default_title: Fallback text if summary not found
        session: Authenticated session object
        
    Returns:
        str: Episode summary or default title if not found
    """
    content = _fetch_page_content(overcast_url, session)
    if not content:
        return default_title
        
    summary_pattern = 'meta name="og:description" content="(.*)"'
    matches = re.findall(summary_pattern, content)
    
    if matches and matches[0]:
        return matches[0]
        
    return default_title

def _fetch_page_content(url: str, session: requests.Session) -> Optional[str]:
    """Helper function to fetch page content"""
    try:
        return session.get(url).text
    except requests.RequestException as e:
        logger.error(f"Failed to fetch page content from {url}: {str(e)}")
        return None 