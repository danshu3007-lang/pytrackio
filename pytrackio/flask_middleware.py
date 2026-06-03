import time

from flask import g, request

from ._registry import _REGISTRY


class FlaskPerformanceTracker:
    """
    Flask extension for automatically tracking HTTP request performance.

    Records each request in pytrackio's metrics registry using the metric name:
    flask.request.<METHOD> <PATH>

    Example:
        flask.request.GET /dashboard
        flask.request.POST /login
    """

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)
        return app

    def before_request(self):
        """Store the start time before Flask handles the request."""
        g.pytrackio_start_time = time.perf_counter()

    def after_request(self, response):
        """Record successful request duration and add it to response headers."""
        if hasattr(g, "pytrackio_start_time"):
            duration_ms = (time.perf_counter() - g.pytrackio_start_time) * 1000
            metric_name = f"flask.request.{request.method} {request.path}"

            _REGISTRY.record(
                metric_name,
                duration_ms,
                error=response.status_code >= 500,
            )

            response.headers["X-Request-Duration-MS"] = f"{duration_ms:.2f}"
            g.pytrackio_recorded = True

        return response

    def teardown_request(self, exception=None):
        """Record failed requests when Flask exits with an exception."""
        if exception is None:
            return

        if hasattr(g, "pytrackio_start_time") and not getattr(g, "pytrackio_recorded", False):
            duration_ms = (time.perf_counter() - g.pytrackio_start_time) * 1000
            metric_name = f"flask.request.{request.method} {request.path}"

            _REGISTRY.record(
                metric_name,
                duration_ms,
                error=True,
            )


def init_pytrackio(app):
    """
    Register pytrackio request performance tracking on a Flask app.

    Example:
        from flask import Flask
        from pytrackio.flask_middleware import init_pytrackio

        app = Flask(__name__)
        init_pytrackio(app)
    """
    tracker = FlaskPerformanceTracker(app)
    return tracker