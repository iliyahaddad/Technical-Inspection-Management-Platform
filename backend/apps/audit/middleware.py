from threading import local

_thread_local = local()


def get_current_request():
    return getattr(_thread_local, "request", None)


class AuditMiddleware:
    """Expose the current request to model signals; always cleared to avoid leaking between requests."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_local.request = request
        try:
            return self.get_response(request)
        finally:
            _thread_local.request = None
