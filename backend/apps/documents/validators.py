"""Upload validation: size, extension and magic-byte signature (extension alone is not a security control)."""
import os
from django.conf import settings

from django.core.exceptions import ValidationError

MAX_UPLOAD_BYTES = 25 * 1024 * 1024

ALLOWED_EXTENSIONS = ("pdf", "doc", "docx", "xls", "xlsx", "png", "jpg", "jpeg", "txt")

_SIGNATURES = {
    "pdf": (b"%PDF-",),
    "png": (b"\x89PNG\r\n\x1a\n",),
    "jpg": (b"\xff\xd8\xff",),
    "jpeg": (b"\xff\xd8\xff",),
    "docx": (b"PK\x03\x04",),
    "xlsx": (b"PK\x03\x04",),
    "doc": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
    "xls": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
}


def validate_upload(uploaded, allowed=ALLOWED_EXTENSIONS):
    """Raise ValidationError unless the upload is within size limits and its content matches its extension."""
    if getattr(uploaded, "_committed", False):  # already stored (e.g. admin full_clean): scanned when it was uploaded
        return uploaded
    ext = os.path.splitext(uploaded.name)[1].lower().lstrip(".")
    if ext not in allowed:
        raise ValidationError(f"File type '.{ext}' is not allowed.")
    if uploaded.size > MAX_UPLOAD_BYTES:
        raise ValidationError("Maximum upload size is 25 MiB.")
    head = uploaded.read(16)
    uploaded.seek(0)
    if ext == "txt":
        try:
            head_text = uploaded.read(4096)
            head_text.decode("utf-8")
        except UnicodeDecodeError:
            raise ValidationError("Text files must be UTF-8 encoded.")
        finally:
            uploaded.seek(0)
        scan_for_malware(uploaded)
        return uploaded
    signatures = _SIGNATURES.get(ext, ())
    if signatures and not any(head.startswith(sig) for sig in signatures):
        raise ValidationError("File content does not match its extension.")
    scan_for_malware(uploaded)
    return uploaded


def scan_for_malware(uploaded):
    """Scan an uploaded file with ClamAV when explicitly enabled. Fail closed when scanning is enabled."""
    if not getattr(settings, 'MALWARE_SCAN_ENABLED', False):
        return
    try:
        import clamd
        client = clamd.ClamdNetworkSocket(host=settings.CLAMAV_HOST, port=settings.CLAMAV_PORT, timeout=settings.CLAMAV_TIMEOUT)
        client.ping()
        uploaded.seek(0)
        result = client.instream(uploaded.file)
        uploaded.seek(0)
        status = (result or {}).get('stream', ['UNKNOWN', ''])[0]
        if status != 'OK':
            raise ValidationError('The uploaded file failed the malware scan.')
    except ValidationError:
        raise
    except Exception as exc:
        raise ValidationError('Malware scanning service is unavailable. Upload rejected for safety.') from exc
