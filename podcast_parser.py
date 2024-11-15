import requests
from xml.etree import ElementTree
from datetime import datetime
from dateutil.tz import gettz
from scraper import get_artwork_url, get_episode_summary
from dateutil.parser import parse as parse_dt

DAYS_TO_KEEP = 1

def parse_opml(response):
    """Parse the OPML response and find all podcasts"""
    text = response.text if isinstance(response, requests.Response) else response
    tree = ElementTree.fromstring(text)
    return tree.findall(".//*[@type='rss']")

def process_podcasts(podcasts, session):
    """Process all podcasts to find recently played episodes"""
    warsaw_tz = gettz('Europe/Warsaw')
    now = datetime.now(warsaw_tz)
    return [process_podcast(podcast, now, session) for podcast in podcasts]

def process_podcast(podcast, now, session):
    """Process a single podcast and its episodes"""
    pod_title = podcast.attrib['title']
    episodes = list(podcast)
    
    artwork_url = _get_podcast_artwork(episodes, session) if episodes else ''
    processed_episodes = [
        process_episode(episode, now, session)
        for episode in episodes
        if should_process_episode(episode, now)
    ]
            
    warsaw_tz = gettz('Europe/Warsaw')
    return {
        "podcast_title": pod_title,
        "artwork_url": artwork_url,
        "episodes": processed_episodes,
        "created_at": datetime.now(warsaw_tz).isoformat(),
        "source": "overcast"
    }

def _get_podcast_artwork(episodes, session):
    """Get artwork URL for podcast from first episode"""
    overcast_url = episodes[0].attrib['overcastUrl']
    return get_artwork_url(overcast_url, session)

def process_episode(episode, now, session):
    """Process a single episode and extract its details"""
    warsaw_tz = gettz('Europe/Warsaw')
    attrs = episode.attrib
    
    user_activity_date_raw = attrs.get('userUpdatedDate')
    last_played_at = (
        parse_dt(user_activity_date_raw).astimezone(warsaw_tz).isoformat()
        if user_activity_date_raw else None
    )

    published = parse_dt(attrs['pubDate']).astimezone(warsaw_tz)
    summary = get_episode_summary(attrs['overcastUrl'], attrs['title'], session)

    return {
        "episode_title": attrs['title'],
        "audio_url": attrs['url'],
        "overcast_url": attrs['overcastUrl'],
        "overcast_id": attrs['overcastId'],
        "published_date": published.isoformat(),
        "play_progress": attrs.get('progress'),
        "last_played_at": last_played_at,
        "summary": summary
    }

def should_process_episode(episode, now):
    """Check if an episode should be processed based on play status and recency"""
    if episode.attrib.get('played', '0') != '1':
        return False
        
    warsaw_tz = gettz('Europe/Warsaw')
    user_activity_date = parse_dt(episode.attrib['userUpdatedDate']).astimezone(warsaw_tz)
    days_since_played = (now - user_activity_date).days
    return days_since_played <= DAYS_TO_KEEP