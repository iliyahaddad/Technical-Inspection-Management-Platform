import mimetypes
import os
from urllib.parse import quote

from django.conf import settings
from django.http import FileResponse, HttpResponse
from rest_framework import status
from rest_framework.response import Response


def protected_file_response(fieldfile, filename=None):
    """Stream a stored file after the caller has already authorised access.

    In production nginx serves the bytes through an internal location (X-Accel-Redirect) so Django
    workers are not tied up; in development Django streams the file itself.
    """
    if not fieldfile:
        return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)
    name = filename or os.path.basename(fieldfile.name)
    content_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
    disposition = f"attachment; filename*=UTF-8''{quote(name)}"
    if getattr(settings, "USE_X_ACCEL_REDIRECT", False):
        response = HttpResponse(content_type=content_type)
        response["X-Accel-Redirect"] = settings.X_ACCEL_REDIRECT_PREFIX + fieldfile.name.lstrip("/")
    else:
        try:
            response = FileResponse(fieldfile.open("rb"), content_type=content_type)
        except FileNotFoundError:
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)
    response["Content-Disposition"] = disposition
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response
