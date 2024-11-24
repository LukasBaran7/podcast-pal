"""Authentication and session management"""
import os
import logging
import requests
from typing import Optional
from ..core.exceptions import AuthenticationError

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        pass
        
    def get_session(self) -> requests.Session:
        """Get an authenticated session"""
        return self._create_new_session()
        
    def _create_new_session(self) -> requests.Session:
        """Create and authenticate a new session"""
        logger.info('Creating new session')
        session = requests.Session()
        
        credentials = self._get_credentials()
        response = session.post('https://overcast.fm/login', data=credentials)

        if response.status_code != 200:
            raise AuthenticationError('Authentication failed')

        logger.info('Authenticated successfully')
        return session
            
    def _get_credentials(self) -> dict:
        """Get credentials from environment variables"""
        email = os.getenv('EMAIL')
        password = os.getenv('PASSWORD')
        
        if not email or not password:
            raise AuthenticationError("Missing EMAIL or PASSWORD environment variables")
            
        return {'email': email, 'password': password}