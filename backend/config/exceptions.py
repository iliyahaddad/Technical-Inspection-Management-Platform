import logging

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("api.errors")


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {"error": True, "detail": response.data}
        return response
    # Unhandled exception: DRF would otherwise swallow it silently. Log with traceback,
    # never leak internals to clients outside DEBUG.
    view = context.get("view")
    logger.exception("Unhandled API exception in %s", view.__class__.__name__ if view else "?", exc_info=exc)
    detail = str(exc) if settings.DEBUG else "Internal server error."
    return Response({"error": True, "detail": detail}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
