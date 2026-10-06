from django.conf import settings
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from config.access_control import INTERNAL_2FA_ROLES, needs_2fa, user_roles


def _eligible(user):
    return bool(user.is_staff or user.is_superuser or user_roles(user) & INTERNAL_2FA_ROLES)


class _TwoFactorView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'  # TOTP guessing is brute force too


class Status2FAView(_TwoFactorView):
    throttle_classes = []

    def get(self, request):
        device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()
        return Response({'enabled': bool(device), 'required': needs_2fa(request.user), 'eligible': _eligible(request.user)})


class Setup2FAView(_TwoFactorView):
    def post(self, request):
        if not _eligible(request.user):
            return Response({'detail': '2FA setup is restricted to internal roles.'}, status=status.HTTP_403_FORBIDDEN)
        if TOTPDevice.objects.filter(user=request.user, confirmed=True).exists():
            return Response({'detail': '2FA is already enabled.'}, status=status.HTTP_400_BAD_REQUEST)
        # A pending (unconfirmed) device is replaced so an abandoned enrolment never leaks an old secret.
        TOTPDevice.objects.filter(user=request.user, confirmed=False).delete()
        device = TOTPDevice.objects.create(user=request.user, name='primary', confirmed=False)
        return Response({'secret': device.key, 'provisioning_uri': device.config_url})


class Verify2FAView(_TwoFactorView):
    def post(self, request):
        device = TOTPDevice.objects.filter(user=request.user).order_by('-confirmed').first()
        token = str(request.data.get('token', '')).strip()
        if not device or not token or not device.verify_token(token):
            return Response({'detail': 'Invalid authentication code.'}, status=status.HTTP_400_BAD_REQUEST)
        if not device.confirmed:
            device.confirmed = True
            device.save(update_fields=['confirmed'])
        return Response({'enabled': True})


class Disable2FAView(_TwoFactorView):
    def post(self, request):
        if getattr(settings, 'INTERNAL_2FA_REQUIRED', False) and needs_2fa(request.user):
            return Response({'detail': '2FA is mandatory for your role and cannot be disabled.'}, status=status.HTTP_403_FORBIDDEN)
        if not request.user.check_password(request.data.get('password', '')):
            return Response({'detail': 'Invalid password.'}, status=status.HTTP_400_BAD_REQUEST)
        device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()
        token = str(request.data.get('token', '')).strip()
        if not device or not device.verify_token(token):
            return Response({'detail': 'Invalid authentication code.'}, status=status.HTTP_400_BAD_REQUEST)
        TOTPDevice.objects.filter(user=request.user).delete()
        return Response({'enabled': False})
