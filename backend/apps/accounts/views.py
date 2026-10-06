from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.serializers import ChangePasswordSerializer, UserCreateSerializer, UserSerializer

User = get_user_model()


class SecureTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Password + (for enrolled internal users) a TOTP code. Enrolment itself is enforced by RoleAndScopePermission."""

    def validate(self, attrs):
        data = super().validate(attrs)
        from config.access_control import has_confirmed_totp, needs_2fa
        device = TOTPDevice.objects.filter(user=self.user, confirmed=True).first()
        # Enrolled users are always challenged (even if the global switch is off): a second factor
        # that can be skipped is not a second factor.
        if device is not None:
            token = str(self.initial_data.get('otp', '')).strip()
            if not token or not device.verify_token(token):
                from rest_framework.exceptions import AuthenticationFailed
                raise AuthenticationFailed('A valid one-time password is required for this account.', code='otp_required')
        data['requires_2fa_setup'] = bool(needs_2fa(self.user) and device is None)
        return data


class LoginView(TokenObtainPairView):
    serializer_class = SecureTokenObtainPairSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login' 


class LogoutView(APIView):
    """Blacklist the supplied refresh token so a stolen token cannot be reused after logout."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response({'refresh': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Never expose the full user directory or another user's profile to ordinary accounts.
        if self.request.user.is_staff or self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.pk)

    def get_permissions(self):
        if self.action == 'create':
            # Self-service signup is disabled for internal inspection systems unless explicitly enabled.
            if getattr(settings, 'ENABLE_PUBLIC_REGISTRATION', False):
                return [AllowAny()]
            return [IsAdminUser()]
        if self.action in {'list', 'destroy'}:
            return [IsAdminUser()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Incorrect password.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])
        return Response({'detail': 'Password updated successfully.'})
