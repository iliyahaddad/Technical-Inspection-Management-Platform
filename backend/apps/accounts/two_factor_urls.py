from django.urls import path
from .two_factor_views import Setup2FAView, Verify2FAView, Disable2FAView, Status2FAView

urlpatterns = [
    path('status/', Status2FAView.as_view()),
    path('setup/', Setup2FAView.as_view()),
    path('verify/', Verify2FAView.as_view()),
    path('disable/', Disable2FAView.as_view()),
]
