import re
import logging

logger = logging.getLogger(__name__)

def _fetch_page_content(url, session):
    """Helper function to fetch page content"""
    try:
        return session.get(url).text
    except Exception as e:
        logger.error(f"Failed to fetch page content from {url}: {str(e)}")
        return None

def get_artwork_url(overcast_url, session):
    """
    Fetch the episode artwork URL from Overcast page.
    
    Args:
        overcast_url: URL of the episode page
        session: Authenticated session object
        
    Returns:
        str: URL of artwork image, or empty string if not found
    """
    content = _fetch_page_content(overcast_url, session)
    if not content:
        return ''
        
    artwork_pattern = 'img class="art fullart" src="(.*)"'
    matches = re.findall(artwork_pattern, content)
    
    if matches:
        return matches[0]
        
    logger.warning(f"Could not find artwork URL for {overcast_url}")
    return ''

def get_episode_summary(overcast_url, default_title, session):
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
