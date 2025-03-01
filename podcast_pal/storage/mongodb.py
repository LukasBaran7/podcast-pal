"""MongoDB storage operations"""
import os
import logging
from typing import Dict, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from ..core.exceptions import StorageError
from ..core.podcast import Podcast
from bson import CodecOptions
import html
from datetime import datetime

logger = logging.getLogger(__name__)

def _serialize_podcast(podcast: Podcast) -> Dict[str, Any]:
    """Serialize podcast object for MongoDB storage"""
    return {
        "podcast_title": podcast.title,
        "artwork_url": podcast.artwork_url,
        "source": podcast.source,
        "created_at": podcast.created_at,
        "category": podcast.category,
        "episodes": [_serialize_episode(episode) for episode in podcast.episodes]
    }

def _serialize_episode(episode) -> Dict[str, Any]:
    """Serialize episode object for MongoDB storage"""
    return {
        "title": episode.title,
        "audio_url": episode.audio_url,
        "overcast_url": episode.overcast_url,
        "overcast_id": episode.overcast_id,
        "published_date": episode.published_date,
        "play_progress": episode.play_progress,
        "last_played_at": episode.last_played_at,
        "summary": html.unescape(episode.summary),
        "duration": episode.duration
    }

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
        logger.error(f"Failed to update podcast: {str(e)}")
        raise StorageError(f"Failed to update podcast: {str(e)}")

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
    logger.debug(f"New episodes to add for podcast '{podcast.title}': {[ep.overcast_id for ep in new_episodes]}")
    collection.update_one(
        {"_id": existing["_id"]},
        {
            "$push": {
                "episodes": {
                    "$each": [_serialize_episode(ep) for ep in new_episodes]
                }
            },
            "$set": {"created_at": podcast.created_at}
        }
    )
    logger.debug(f"Successfully updated podcast '{podcast.title}' with new episodes.")
    return True

def _insert_new_podcast(collection: Collection, podcast: Podcast) -> bool:
    """Insert a new podcast into the collection"""
    logger.info(f"Inserting new podcast '{podcast.title}' with {len(podcast.episodes)} episodes")
    collection.insert_one(_serialize_podcast(podcast))
    return True

def get_mongodb_collection() -> Collection:
    """Initialize and return MongoDB collection"""
    config = _get_mongodb_config()
    client = MongoClient(config['uri'])
    db = client[config['db']]
    codec_options = CodecOptions(
        document_class=dict,
        tz_aware=True,
        unicode_decode_error_handler='replace'
    )
    collection = db.get_collection(config['collection'], codec_options=codec_options)
    
    logger.info(f"Connected to MongoDB collection '{config['db']}.{config['collection']}'")
    return collection

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