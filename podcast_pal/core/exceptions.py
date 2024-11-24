"""Custom exceptions for the podcast_pal package"""

class PodcastPalError(Exception):
    """Base exception for all podcast_pal errors"""
    pass

class FetchError(PodcastPalError):
    """Raised when fetching data fails"""
    pass

class AuthenticationError(PodcastPalError):
    """Raised when authentication fails"""
    pass

class StorageError(PodcastPalError):
    """Raised when storage operations fail"""
    pass 