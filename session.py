import os
import sys
import pickle
import requests
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def _load_saved_session(session_path):
    """Load and return a previously saved session"""
    logger.info('Found saved session. Restoring!')
    with open(session_path, 'rb') as f:
        return pickle.loads(f.read())

def _create_new_session(session_path):
    """Create, authenticate and save a new session"""
    logger.info('No saved session. Authenticating!')
    session = requests.Session()
    
    response = session.post('https://overcast.fm/login', data={
        'email': os.getenv('EMAIL'),
        'password': os.getenv('PASSWORD')
    })

    if response.status_code != 200:
        logger.error('Authentication failed')
        sys.exit(1)

    logger.info('Authenticated successfully. Saving session.')
    
    with open(session_path, 'wb') as f:
        pickle.dump(session, f)
        
    return session

def get_authenticated_session():
    """Get an authenticated session, either from cache or by logging in"""
    load_dotenv()
    session_path = os.getenv('SESSION_PATH')
    
    if os.path.exists(session_path):
        return _load_saved_session(session_path)
    return _create_new_session(session_path)