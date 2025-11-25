import datetime
import logging

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