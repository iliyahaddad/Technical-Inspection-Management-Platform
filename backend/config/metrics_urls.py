from django.urls import path
from .metrics import metrics

urlpatterns = [path('', metrics, name='metrics')]
