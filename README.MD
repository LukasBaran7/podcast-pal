# PodcastPal

PodcastPal is a Python application that helps you track and analyze your Overcast podcast listening history. It fetches your recently played episodes, enriches them with additional metadata, and stores them in MongoDB for analysis.

## Features

- Fetches recently played episodes from Overcast
- Extracts episode metadata like artwork, summaries, and play progress 
- Caches OPML data to reduce API calls
- Stores enriched podcast data in MongoDB
- Handles authentication and session management
- Tracks listening progress and history over time
- Supports multiple podcast platforms
- Provides data export capabilities
- Includes detailed episode metadata
- Offers podcast analytics and insights

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   - Create a `.env` file with the following content:
     ```
     PODCAST_DB=your_podcast_db_connection_string
     EMAIL=your_overcast_email
     PASSWORD=your_overcast_password
     SESSION_PATH=overcast_session.pkl
     MONGODB_DATABASE=my_podcast_library
     MONGODB_COLLECTION=episode_history
     ```
   - Add your Overcast credentials
   - Configure MongoDB connection details

3. Initialize the database:
   ```bash
   python init_db.py
   ```

4. Run the application:
   ```bash
   python enriched_overcast_parser.py
   ```
