"""MongoDB storage operations"""
import os
import logging
from typing import Dict, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from ..core.exceptions import StorageError
from ..core.podcast import Podcast

logger = logging.getLogger(__name__)

def get_mongodb_collection() -> Collection:
    """Initialize and return MongoDB collection"""
    config = _get_mongodb_config()
    client = MongoClient(config['uri'])
    db = client[config['db']]
    collection = db[config['collection']]
    
    logger.info(f"Connected to MongoDB collection '{config['db']}.{config['collection']}'")
    return collection

def update_podcast(collection: Collection, podcast: Podcast) -> bool:
    """Update a single podcast in MongoDB collection"""
    query = {
        "podcast_title": podcast.title,
        "source": podcast.source
    }
    
    try:
        existing = collection.find_one(query)
        if existing:
            return _update_existing_podcast(collection, existing, podcast)
        return _insert_new_podcast(collection, podcast)
    except Exception as e:
        raise StorageError(f"Failed to update podcast: {str(e)}")

def _get_mongodb_config() -> Dict[str, str]:
    """Get and validate MongoDB configuration from environment"""
    required_vars = {
        'uri': 'PODCAST_DB',
        'db': 'MONGODB_DATABASE',
        'collection': 'MONGODB_COLLECTION'
    }
    
    config = {}
    for key, env_var in required_vars.items():
        value = os.getenv(env_var)
        if not value:
            raise StorageError(f"Missing required environment variable: {env_var}")
        config[key] = value
        
    return config

def _update_existing_podcast(collection: Collection, 
                           existing: Dict[str, Any], 
                           podcast: Podcast) -> bool:
    """Update an existing podcast with new episodes"""
    existing_ids = {ep["overcast_id"] for ep in existing["episodes"]}
    new_episodes = [ep for ep in podcast.episodes 
                   if ep.overcast_id not in existing_ids]
    
    if not new_episodes:
        logger.debug(f"No new episodes for podcast '{podcast.title}'")
        return False
    
    logger.info(f"Updating podcast '{podcast.title}' with {len(new_episodes)} new episodes")
    collection.update_one(
        {"_id": existing["_id"]},
        {
            "$push": {"episodes": {"$each": new_episodes}},
            "$set": {"created_at": podcast.created_at}
        }
    )
    return True

def _insert_new_podcast(collection: Collection, podcast: Podcast) -> bool:
    """Insert a new podcast into the collection"""
    logger.info(f"Inserting new podcast '{podcast.title}' with {len(podcast.episodes)} episodes")
    collection.insert_one(podcast.__dict__)
    return True 