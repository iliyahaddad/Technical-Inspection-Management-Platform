from rest_framework.pagination import PageNumberPagination

from django.conf import settings


class StandardPagination(PageNumberPagination):
    """DRF ignores PAGE_SIZE_QUERY_PARAM / MAX_PAGE_SIZE in settings (they are class attributes), so the
    ``?page_size=`` parameter used by the UI only works with this explicit class."""
    page_size = getattr(settings, 'API_PAGE_SIZE', 50)
    page_size_query_param = 'page_size'
    max_page_size = getattr(settings, 'API_MAX_PAGE_SIZE', 100)
