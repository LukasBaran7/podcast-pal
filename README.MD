# PodcastPal

A Python tool for tracking and analyzing your Overcast podcast listening history.

## Features

- Fetches and parses podcast data from Overcast
- Tracks recently played episodes
- Stores podcast history in MongoDB
- Caches data to minimize API requests
- Type-safe with full type hints

## Installation

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
