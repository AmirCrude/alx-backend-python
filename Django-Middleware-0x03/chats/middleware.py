import datetime
import logging
from django.http import HttpResponseForbidden, JsonResponse
from django.core.cache import cache
import time
import json

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

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        """
        Initialize the middleware
        """
        self.get_response = get_response
        # Define offensive words (you can expand this list)
        self.offensive_words = [
            'badword', 'offensive', 'inappropriate', 'hate', 
            'violence', 'spam', 'stupid', 'idiot'  # Add more as needed
        ]

    def __call__(self, request):
        """
        Check for offensive language in POST requests
        """
        # Only check POST requests for messages/conversations
        if request.method == 'POST' and any(path in request.path for path in ['/api/conversations', '/api/messages']):
            # Check for offensive language in request data
            offensive_found = self.check_offensive_language(request)
            
            if offensive_found:
                return JsonResponse({
                    'error': 'Your message contains inappropriate language and cannot be sent.'
                }, status=400)
        
        response = self.get_response(request)
        return response

    def check_offensive_language(self, request):
        """
        Check request data for offensive language
        """
        # Check POST data
        if request.POST:
            for key, value in request.POST.items():
                if isinstance(value, str):
                    for word in self.offensive_words:
                        if word.lower() in value.lower():
                            return True
        
        # Also check JSON data for API requests
        if request.content_type == 'application/json' and request.body:
            try:
                data = json.loads(request.body)
                # Recursively check all values in JSON data
                return self._check_dict_for_offensive_words(data)
            except json.JSONDecodeError:
                pass
        
        return False

    def _check_dict_for_offensive_words(self, data):
        """
        Recursively check dictionary for offensive words
        """
        if isinstance(data, dict):
            for value in data.values():
                if self._check_dict_for_offensive_words(value):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self._check_dict_for_offensive_words(item):
                    return True
        elif isinstance(data, str):
            for word in self.offensive_words:
                if word.lower() in data.lower():
                    return True
        return False


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = 5  # 5 POST messages per minute
        self.window_size = 60  # 1 minute in seconds

    def __call__(self, request):
        """
        Count the number of POST requests (messages) from each IP address
        """
        # Only count POST requests to messages/conversations endpoints
        if request.method == 'POST' and any(path in request.path for path in ['/api/messages', '/api/conversations']):
            # Get client IP address
            ip_address = self.get_client_ip(request)
            print(f"Counting POST request from IP: {ip_address} to {request.path}")  # Debug
            
            # Create a unique key for this IP for POST requests
            cache_key = f"post_rate_limit_{ip_address}"
            
            # Get current POST request count and timestamp
            request_data = cache.get(cache_key, {'post_count': 0, 'first_post_request': time.time()})
            print(f"Current POST count: {request_data['post_count']}")  # Debug
            
            # Check if window has expired
            current_time = time.time()
            if current_time - request_data['first_post_request'] > self.window_size:
                # Reset counter - new time window
                request_data = {'post_count': 1, 'first_post_request': current_time}
                print("Reset POST counter - new window")  # Debug
            else:
                # Increment POST counter
                request_data['post_count'] += 1
                print(f"Incremented POST counter to: {request_data['post_count']}")  # Debug
            
            # Check if rate limit exceeded for POST requests
            if request_data['post_count'] > self.rate_limit:
                print(f"POST RATE LIMIT EXCEEDED! IP: {ip_address} made {request_data['post_count']} POST requests")  # Debug
                return JsonResponse({
                    'error': f'Rate limit exceeded. Maximum {self.rate_limit} messages per minute.'
                }, status=429)
            
            # Update cache
            cache.set(cache_key, request_data, self.window_size)
            print(f"POST cache updated. Count: {request_data['post_count']}")  # Debug
        
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip