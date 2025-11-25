import datetime
import logging
from django.http import HttpResponseForbidden

# Set up logging configuration
logger = logging.getLogger('request_logger')
logger.setLevel(logging.INFO)

# Create file handler that will write to requests.log
file_handler = logging.FileHandler('requests.log')
file_handler.setLevel(logging.INFO)

# Create formatter to specify the log message format
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(file_handler)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        """
        Initialize the middleware.
        get_response is the next middleware in the chain or the view
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        This method is called for every request
        """
        # Get user information - handle both authenticated and anonymous users
        user = "Anonymous"
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user.username
        
        # Log the request information
        log_message = f"User: {user} - Path: {request.path}"
        logger.info(log_message)
        
        # Process the request and get response
        response = self.get_response(request)
        
        return response
    
class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        """
        Initialize the middleware
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Check if current time is between 6 PM (18:00) and 9 PM (21:00)
        If yes, block access to chat-related paths
        """
        # Get current time
        current_time = datetime.datetime.now().time()
        start_time = datetime.time(18, 0)  # 6 PM
        end_time = datetime.time(21, 0)    # 9 PM
        
        # Check if current time is between 6 PM and 9 PM
        if start_time <= current_time <= end_time:
            # Check if the request is for conversation/message paths (your actual API structure)
            restricted_paths = ['/api/conversations', '/api/messages']
            if any(request.path.startswith(path) for path in restricted_paths):
                return HttpResponseForbidden(
                    "Chat access is restricted between 6 PM and 9 PM. Please try again later."
                )
        
        # If not restricted time or not chat path, process normally
        response = self.get_response(request)
        return response
