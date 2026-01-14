"""
Error handling and common response utilities
"""

import logging
from typing import Dict, Any, Tuple, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base class for API errors"""
    def __init__(self, message: str, status_code: int = 400, details: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(APIError):
    """Resource not found"""
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", 404)


class ValidationError(APIError):
    """Validation failed"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(f"Validation error: {message}", 422, details)


class UnauthorizedError(APIError):
    """Unauthorized access"""
    def __init__(self, message: str = "Admin required"):
        super().__init__(message, 403)


class ExternalServiceError(APIError):
    """Error from external service (e.g., Semantic Scholar)"""
    def __init__(self, service: str, message: str):
        super().__init__(f"Error from {service}: {message}", 502)


def make_response(data: Any = None, message: str = None, status_code: int = 200) -> Tuple[Dict, int]:
    """
    Create a standardized API response.
    
    Args:
        data: Response data
        message: Optional message
        status_code: HTTP status code
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    response = {
        'success': 200 <= status_code < 300,
        'status_code': status_code,
    }
    
    if message:
        response['message'] = message
    
    if data is not None:
        response['data'] = data
    
    return response, status_code


def make_error_response(error: APIError) -> Tuple[Dict, int]:
    """
    Create a standardized error response from APIError.
    
    Args:
        error: APIError instance
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    response = {
        'success': False,
        'status_code': error.status_code,
        'error': {
            'message': error.message,
            'details': error.details
        }
    }
    
    return response, error.status_code


def safe_external_call(func):
    """
    Decorator for safe external API calls.
    Handles timeouts, rate limits, and other errors gracefully.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionError as e:
            logger.error(f"Connection error in {func.__name__}: {e}")
            raise ExternalServiceError(func.__name__, "Connection failed")
        except TimeoutError as e:
            logger.error(f"Timeout in {func.__name__}: {e}")
            raise ExternalServiceError(func.__name__, "Request timeout")
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise ExternalServiceError(func.__name__, str(e))
    
    return wrapper


def handle_api_errors(func):
    """
    Decorator for endpoint handlers.
    Catches APIError exceptions and converts to proper responses.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            logger.warning(f"API Error in {func.__name__}: {e.message}")
            return make_error_response(e)
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            error = APIError(str(e), 500)
            return make_error_response(error)
    
    return wrapper


def format_pagination(items: list, total: int, page: int, per_page: int) -> Dict:
    """
    Format pagination data for response.
    
    Args:
        items: List of items
        total: Total count
        page: Current page number
        per_page: Items per page
        
    Returns:
        Pagination dictionary
    """
    total_pages = (total + per_page - 1) // per_page
    
    return {
        'items': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }
