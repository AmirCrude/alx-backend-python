from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserBackend(object):
    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom checks can be added here.
        """
        return user.is_active