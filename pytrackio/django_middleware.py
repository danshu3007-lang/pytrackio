import time

from django.utils.deprecation import MiddlewareMixin

from ._registry import _REGISTRY


class RequestPerformanceMiddleware(MiddlewareMixin):
    """
    Django middleware for automatically tracking HTTP request performance.

    Records each request in pytrackio's metrics registry using the metric name:
    django.request.<METHOD> <PATH>

    Example:
        django.request.GET /dashboard
        django.request.POST /login
    """

    def process_request(self, request):
        """Store the start time when a request enters the middleware."""
        request.pytrackio_start_time = time.perf_counter()

    def process_response(self, request, response):
        """Record request duration and add it to the response headers."""
        if hasattr(request, "pytrackio_start_time"):
            duration_ms = (time.perf_counter() - request.pytrackio_start_time) * 1000
            metric_name = f"django.request.{request.method} {request.path}"

            _REGISTRY.record(
                metric_name,
                duration_ms,
                error=response.status_code >= 500,
            )

            response["X-Request-Duration-MS"] = f"{duration_ms:.2f}"

        return response

    def process_exception(self, request, exception):
        """Record failed requests when a view raises an exception."""
        if hasattr(request, "pytrackio_start_time"):
            duration_ms = (time.perf_counter() - request.pytrackio_start_time) * 1000
            metric_name = f"django.request.{request.method} {request.path}"

            _REGISTRY.record(
                metric_name,
                duration_ms,
                error=True,
            )

        return None