"""
Core data models for podcasts and episodes
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, TypeAlias
from xml.etree.ElementTree import Element
import html

# Type alias for raw XML podcast data
RawPodcastData: TypeAlias = Element

@dataclass
class Episode:
    title: str
    audio_url: str
    overcast_url: str
    overcast_id: str
    published_date: datetime
    play_progress: Optional[int]
    last_played_at: Optional[datetime]
    summary: str
    duration: Optional[int] = None  # Duration in seconds

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
            summary=summary,
            duration=int(attrs.get('duration', 0)) if attrs.get('duration') else None
        )

    def to_dict(self):
        # Convert the Episode to a dictionary with proper encoding
        data = asdict(self)
        # Decode HTML entities in the summary
        data['summary'] = html.unescape(data['summary'])
        return data

@dataclass
class Podcast:
    title: str
    artwork_url: str
    episodes: List[Episode]
    created_at: datetime
    source: str = "overcast"
    category: Optional[str] = None  # Podcast category

    @classmethod
    def from_raw_data(cls, raw_data: RawPodcastData, 
                      episodes: List[Episode], 
                      artwork_url: str) -> 'Podcast':
        """Create Podcast instance from raw XML data"""
        return cls(
            title=raw_data.attrib['title'],
            artwork_url=artwork_url,
            episodes=episodes,
            created_at=datetime.now(),
            category=raw_data.attrib.get('category')
        ) 