"""Authentication and session management"""
import os
import pickle
import logging
import requests
from typing import Optional
from ..core.exceptions import AuthenticationError

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, session_path: str):
        self.session_path = session_path
        
    def get_session(self) -> requests.Session:
        """Get an authenticated session, either from cache or by logging in"""
        if os.path.exists(self.session_path):
            return self._load_saved_session()
        return self._create_new_session()
        
    def _load_saved_session(self) -> requests.Session:
        """Load and return a previously saved session"""
        logger.info('Found saved session. Restoring!')
        try:
            with open(self.session_path, 'rb') as f:
                return pickle.loads(f.read())
        except (IOError, pickle.PickleError) as e:
            raise AuthenticationError(f"Failed to load saved session: {str(e)}")
            
    def _create_new_session(self) -> requests.Session:
        """Create, authenticate and save a new session"""
        logger.info('No saved session. Authenticating!')
        session = requests.Session()
        
        credentials = self._get_credentials()
        response = session.post('https://overcast.fm/login', data=credentials)

        if response.status_code != 200:
            raise AuthenticationError('Authentication failed')

        logger.info('Authenticated successfully. Saving session.')
        self._save_session(session)
        return session
        
    def _save_session(self, session: requests.Session) -> None:
        """Save session to file"""
        try:
            with open(self.session_path, 'wb') as f:
                pickle.dump(session, f)
        except IOError as e:
            raise AuthenticationError(f"Failed to save session: {str(e)}")
            
    def _get_credentials(self) -> dict:
        """Get credentials from environment variables"""
        email = os.getenv('EMAIL')
        password = os.getenv('PASSWORD')
        
        if not email or not password:
            raise AuthenticationError("Missing EMAIL or PASSWORD environment variables")
            
        return {'email': email, 'password': password} 