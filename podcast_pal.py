"""
PodcastPal: Your friendly podcast data companion
Helps you track and analyze your Overcast listening history

The main entry point for clients is fetch_and_parse_podcasts(), which returns processed podcast data.
For MongoDB storage, use get_mongodb_collection() and update_podcast_collection().
"""

import logging
import os
import sys
from dotenv import load_dotenv
import requests

from cache import cache_opml, load_cached_opml
from db_helper import get_mongodb_collection, update_podcast_collection
from opml_scraper import fetch_opml, parse_opml
from podcast_parser import parse_opml, process_podcasts
from session import get_authenticated_session

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _fetch_fresh_podcasts(session):
    """Fetch fresh podcast data from Overcast and cache it"""
    logger.info("Fetching fresh OPML data")
    try:
        response = fetch_opml(session)
        if isinstance(response.text, str):  # Only cache if we got actual new data
            cache_opml(response)
        return parse_opml(response)
    except requests.RequestException as e:
        logger.error(f"Failed to fetch fresh data: {e}")
        sys.exit(1)

def fetch_and_parse_podcasts(session):
    """Fetch and parse podcast data from Overcast, using cache if available"""
    cached_opml = load_cached_opml()
    podcasts = parse_opml(cached_opml) if cached_opml else _fetch_fresh_podcasts(session)
    return process_podcasts(podcasts, session)

def main():
    session = get_authenticated_session()
    processed_podcasts = fetch_and_parse_podcasts(session)
    collection = get_mongodb_collection()

    # Save podcasts
    updates_count = sum(
        update_podcast_collection(collection, podcast) 
        for podcast in processed_podcasts
    )

    if updates_count == 0:
        logger.info("No podcasts were updated in this run")
    else:
        logger.info(f"Updated {updates_count} podcasts in this run")

if __name__ == '__main__':
    # Load environment variables first to check if credentials exist
    load_dotenv()
    required_vars = ['EMAIL', 'PASSWORD', 'PODCAST_DB', 'MONGODB_DATABASE', 'MONGODB_COLLECTION']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Please set all required variables in .env file before running")
        sys.exit(1)
        
    main()
