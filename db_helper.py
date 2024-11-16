import os
from dotenv import load_dotenv
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)

def get_mongodb_collection():
    """Initialize and return MongoDB collection"""
    load_dotenv()
    
    # Get required environment variables
    config = {
        'uri': ('PODCAST_DB', 'MongoDB connection URI'),
        'db': ('MONGODB_DATABASE', 'Database name'), 
        'collection': ('MONGODB_COLLECTION', 'Collection name')
    }
    
    # Validate all required env vars exist
    settings = {}
    for key, (env_var, description) in config.items():
        value = os.getenv(env_var)
        if not value:
            raise ValueError(f"{env_var} environment variable is not set ({description})")
        settings[key] = value

    # Connect to MongoDB using validated settings
    client = MongoClient(settings['uri'])
    db = client[settings['db']]
    collection = db[settings['collection']]
    
    logger.info(f"Connected to MongoDB collection '{settings['db']}.{settings['collection']}'")
    return collection

def update_podcast_collection(collection, podcast):
    """Update a single podcast in MongoDB collection"""
    query = {
        "podcast_title": podcast["podcast_title"],
        "source": "overcast"
    }
    
    existing = collection.find_one(query)
    if existing:
        return _update_existing_podcast(collection, existing, podcast)
    else:
        return _insert_new_podcast(collection, podcast)

def _update_existing_podcast(collection, existing, podcast):
    """Update an existing podcast with any new episodes"""
    # Find episodes that don't exist in the current document
    new_episodes = _get_new_episodes(existing, podcast)
    
    if not new_episodes:
        logger.debug(f"No new episodes found for podcast '{podcast['podcast_title']}'")
        return False
    
    # Update document with new episodes
    _update_podcast_document(collection, existing, podcast, new_episodes)
    return True

def _get_new_episodes(existing, podcast):
    """Get episodes that don't exist in the current document"""
    existing_ids = {ep["overcast_id"] for ep in existing["episodes"]}
    return [ep for ep in podcast["episodes"] 
            if ep["overcast_id"] not in existing_ids]

def _update_podcast_document(collection, existing, podcast, new_episodes):
    """Update MongoDB document with new episodes"""
    logger.info(f"Updating podcast '{podcast['podcast_title']}' with {len(new_episodes)} new episodes")
    collection.update_one(
        {"_id": existing["_id"]},
        {
            "$push": {"episodes": {"$each": new_episodes}},
            "$set": {"created_at": podcast["created_at"]}
        }
    )

def _insert_new_podcast(collection, podcast):
    """Insert a new podcast into the collection"""
    logger.info(f"Inserting new podcast '{podcast['podcast_title']}' with {len(podcast['episodes'])} episodes")
    collection.insert_one(podcast)
    return True
