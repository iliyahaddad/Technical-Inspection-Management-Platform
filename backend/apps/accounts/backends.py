from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from guardian.backends import ObjectPermissionBackend

User = get_user_model()

class InspectionPlatformBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        try:
            user = User.objects.get(email=username)
            if user.check_password(password) and user.is_active:
                return user
        except User.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return None
