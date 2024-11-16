"""
Core data models for podcasts and episodes
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, TypeAlias
from xml.etree.ElementTree import Element

# Type alias for raw XML podcast data
RawPodcastData: TypeAlias = Element

@dataclass
class Episode:
    title: str
    audio_url: str
    overcast_url: str
    overcast_id: str
    published_date: datetime
    play_progress: Optional[str]
    last_played_at: Optional[datetime]
    summary: str

    @classmethod
    def from_raw_data(cls, raw_data: Element, summary: str) -> 'Episode':
        """Create Episode instance from raw XML data"""
        attrs = raw_data.attrib
        return cls(
            title=attrs['title'],
            audio_url=attrs['url'],
            overcast_url=attrs['overcastUrl'],
            overcast_id=attrs['overcastId'],
            published_date=datetime.fromisoformat(attrs['pubDate']),
            play_progress=attrs.get('progress'),
            last_played_at=datetime.fromisoformat(attrs['userUpdatedDate']) 
                if attrs.get('userUpdatedDate') else None,
            summary=summary
        )

@dataclass
class Podcast:
    title: str
    artwork_url: str
    episodes: List[Episode]
    created_at: datetime
    source: str = "overcast"

    @classmethod
    def from_raw_data(cls, raw_data: RawPodcastData, 
                      episodes: List[Episode], 
                      artwork_url: str) -> 'Podcast':
        """Create Podcast instance from raw XML data"""
        return cls(
            title=raw_data.attrib['title'],
            artwork_url=artwork_url,
            episodes=episodes,
            created_at=datetime.now()
        ) 