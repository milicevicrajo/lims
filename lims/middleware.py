import datetime
from django.conf import settings
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import PermissionDenied
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
import logging

class AutoLogout(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        current_datetime = datetime.datetime.now()
        last_activity = request.session.get('last_activity')

        if last_activity:
            # Convert the stored string back to a datetime object
            last_activity = datetime.datetime.fromisoformat(last_activity)
            elapsed_time = (current_datetime - last_activity).total_seconds()
            if elapsed_time > settings.SESSION_COOKIE_AGE:
                logout(request)
                return

        # Store the current datetime as a string
        request.session['last_activity'] = current_datetime.isoformat()

class RestrictIPMiddleware(MiddlewareMixin):
    ALLOWED_IPS = ['127.0.0.1','www.imslims.site', 'imslims.site', '185.166.39.94']  # List of allowed IP addresses

    def process_request(self, request):
        ip = request.META.get('REMOTE_ADDR')
        if ip not in self.ALLOWED_IPS:
            raise PermissionDenied
        
User = get_user_model()
logger = logging.getLogger('django')

class OneSessionPerUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            current_session_key = request.session.session_key
            user = request.user

            if user.session_key and user.session_key != current_session_key:
                # Terminate the previous session
                try:
                    Session.objects.get(session_key=user.session_key).delete()
                except Session.DoesNotExist:
                    pass

            # Update the session key in the user model
            user.session_key = current_session_key
            user.save()

class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response