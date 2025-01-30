"""Core podcast processing functionality"""
import logging
from datetime import datetime
from typing import List
from dateutil.tz import gettz
from dateutil.parser import parse as parse_dt

from .core.podcast import Podcast, Episode, RawPodcastData
from .fetchers.artwork import get_artwork_url
from .fetchers.summary import get_episode_summary

logger = logging.getLogger(__name__)

DAYS_TO_KEEP = 3

def process_podcasts(raw_podcasts: List[RawPodcastData], session) -> tuple[List[Podcast], List[Podcast]]:
    """Process all podcasts to find both played and unplayed episodes"""
    warsaw_tz = gettz('Europe/Warsaw')
    now = datetime.now(warsaw_tz)
    played_podcasts = []
    unplayed_podcasts = []
    
    for raw_podcast in raw_podcasts:
        played, unplayed = process_podcast(raw_podcast, now, session)
        if played.episodes:
            played_podcasts.append(played)
        if unplayed.episodes:
            unplayed_podcasts.append(unplayed)
            
    return played_podcasts, unplayed_podcasts

def process_podcast(raw_podcast: RawPodcastData, now: datetime, session, 
                   days_to_keep: int = DAYS_TO_KEEP) -> tuple[Podcast, Podcast]:
    """Process a single podcast and separate played/unplayed episodes"""
    episodes = list(raw_podcast)
    artwork_url = get_podcast_artwork(episodes, session) if episodes else ''
    
    played_episodes = []
    unplayed_episodes = []
    
    for episode in episodes:
        processed_episode = process_episode(episode, session)
        if episode.attrib.get('played', '0') == '1':
            if should_process_played_episode(episode, now, days_to_keep):
                played_episodes.append(processed_episode)
        else:
            unplayed_episodes.append(processed_episode)
    
    played_podcast = Podcast.from_raw_data(raw_podcast, played_episodes, artwork_url)
    unplayed_podcast = Podcast.from_raw_data(raw_podcast, unplayed_episodes, artwork_url)
    return played_podcast, unplayed_podcast

def get_podcast_artwork(episodes: List[RawPodcastData], session) -> str:
    """Get artwork URL for podcast from first episode"""
    overcast_url = episodes[0].attrib['overcastUrl']
    return get_artwork_url(overcast_url, session)

def process_episode(raw_episode: RawPodcastData, session) -> Episode:
    """Process a single episode and extract its details"""
    summary = get_episode_summary(
        raw_episode.attrib['overcastUrl'],
        raw_episode.attrib['title'],
        session
    )
    return Episode.from_raw_data(raw_episode, summary)

def should_process_played_episode(episode: RawPodcastData, now: datetime, 
                                days_to_keep: int = DAYS_TO_KEEP) -> bool:
    """Check if a played episode should be processed based on recency"""
    warsaw_tz = gettz('Europe/Warsaw')
    if now.tzinfo is None:
        now = now.replace(tzinfo=warsaw_tz)
        
    user_activity_date = parse_dt(episode.attrib['userUpdatedDate'])
    if user_activity_date.tzinfo is None:
        user_activity_date = user_activity_date.replace(tzinfo=warsaw_tz)
    else:
        user_activity_date = user_activity_date.astimezone(warsaw_tz)
        
    days_since_played = (now - user_activity_date).days
    return days_since_played <= days_to_keep 