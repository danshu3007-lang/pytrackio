from django.conf import settings

if not settings.configured:
    settings.configure(
        DEFAULT_CHARSET="utf-8",
        SECRET_KEY="test-secret-key",
        ALLOWED_HOSTS=["*"],
    )

from django.http import HttpResponse
from django.test import RequestFactory

from pytrackio import get_registry
from pytrackio.django_middleware import RequestPerformanceMiddleware


def test_django_middleware_tracks_successful_request():
    registry = get_registry()
    registry.reset()

    request = RequestFactory().get("/hello")

    def get_response(request):
        return HttpResponse("ok", status=200)

    middleware = RequestPerformanceMiddleware(get_response)
    response = middleware(request)

    summary = registry.summary("django.request.GET /hello")

    assert response.status_code == 200
    assert "X-Request-Duration-MS" in response
    assert summary is not None
    assert summary.calls == 1
    assert summary.errors == 0


def test_django_middleware_tracks_server_error_response():
    registry = get_registry()
    registry.reset()

    request = RequestFactory().get("/error")

    def get_response(request):
        return HttpResponse("error", status=500)

    middleware = RequestPerformanceMiddleware(get_response)
    response = middleware(request)

    summary = registry.summary("django.request.GET /error")

    assert response.status_code == 500
    assert summary is not None
    assert summary.calls == 1
    assert summary.errors == 1