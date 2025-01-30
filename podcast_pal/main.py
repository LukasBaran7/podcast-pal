"""
PodcastPal: Your friendly podcast data companion
Helps you track and analyze your Overcast listening history
"""

import logging
import os
import sys
from typing import List
from dotenv import load_dotenv

from podcast_pal.core.podcast import Podcast
from podcast_pal.core.exceptions import PodcastPalError
from podcast_pal.auth.session import SessionManager
from podcast_pal.fetchers.opml import fetch_opml, parse_opml
from podcast_pal.processor import process_podcasts
from podcast_pal.storage.cache import load_cached_opml
from podcast_pal.storage.mongodb import get_mongodb_collections, update_podcast

# Configure more detailed logging
logging.basicConfig(
    level=logging.INFO,  # Changed from INFO to DEBUG to see more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def fetch_and_parse_podcasts(session_manager) -> List[Podcast]:
    """Fetch and parse podcast data from Overcast, using cache if available"""
    session = session_manager.get_session()
    cached_opml = load_cached_opml()
    
    if cached_opml:
        raw_podcasts = parse_opml(cached_opml)
    else:
        response = fetch_opml(session)
        raw_podcasts = parse_opml(response.text)
    
    return process_podcasts(raw_podcasts, session)

def main():
    """Main entry point for the application"""
    try:
        # Initialize session
        session_manager = SessionManager()
        
        # Process podcasts
        played_podcasts, unplayed_podcasts = fetch_and_parse_podcasts(session_manager)
        played_collection, unplayed_collection = get_mongodb_collections()

        # Save played podcasts
        played_updates = sum(
            update_podcast(played_collection, podcast) 
            for podcast in played_podcasts
        )

        # Save unplayed podcasts
        unplayed_updates = sum(
            update_podcast(unplayed_collection, podcast)
            for podcast in unplayed_podcasts
        )

        if played_updates == 0 and unplayed_updates == 0:
            logger.info("No podcasts were updated in this run")
        else:
            logger.info(f"Updated {played_updates} played podcasts and {unplayed_updates} unplayed podcasts in this run")
            
    except PodcastPalError as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        sys.exit(1)

def check_environment():
    """Check if all required environment variables are set"""
    load_dotenv()
    required_vars = [
        'EMAIL', 'PASSWORD', 'PODCAST_DB', 
        'MONGODB_DATABASE', 'MONGODB_COLLECTION'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Please set all required variables in .env file before running")
        sys.exit(1)

if __name__ == '__main__':
    check_environment()
    main()