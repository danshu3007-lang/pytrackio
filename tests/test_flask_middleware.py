from flask import Flask

from pytrackio import get_registry
from pytrackio.flask_middleware import FlaskPerformanceTracker, init_pytrackio


def test_flask_middleware_tracks_successful_request():
    registry = get_registry()
    registry.reset()

    app = Flask(__name__)
    FlaskPerformanceTracker(app)

    @app.get("/hello")
    def hello():
        return "ok"

    response = app.test_client().get("/hello")
    summary = registry.summary("flask.request.GET /hello")

    assert response.status_code == 200
    assert "X-Request-Duration-MS" in response.headers
    assert summary is not None
    assert summary.calls == 1
    assert summary.errors == 0


def test_flask_middleware_tracks_server_error_response():
    registry = get_registry()
    registry.reset()

    app = Flask(__name__)
    init_pytrackio(app)

    @app.get("/error")
    def error():
        return "error", 500

    response = app.test_client().get("/error")
    summary = registry.summary("flask.request.GET /error")

    assert response.status_code == 500
    assert summary is not None
    assert summary.calls == 1
    assert summary.errors == 1