from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

import main


def _protected_app():
    async def home(request):
        return PlainTextResponse("ok")

    return Starlette(
        routes=[Route("/", home)],
        middleware=[Middleware(main.APIKeyMiddleware)],
    )


def test_rejects_request_with_no_key(monkeypatch):
    monkeypatch.setattr(main, "API_KEY", "secret")
    client = TestClient(_protected_app())

    response = client.get("/")

    assert response.status_code == 401


def test_rejects_request_with_wrong_key(monkeypatch):
    monkeypatch.setattr(main, "API_KEY", "secret")
    client = TestClient(_protected_app())

    response = client.get("/", headers={"x-api-key": "wrong"})

    assert response.status_code == 401


def test_accepts_request_with_correct_key(monkeypatch):
    monkeypatch.setattr(main, "API_KEY", "secret")
    client = TestClient(_protected_app())

    response = client.get("/", headers={"x-api-key": "secret"})

    assert response.status_code == 200
    assert response.text == "ok"


def test_fails_closed_when_server_key_is_unconfigured(monkeypatch):
    """Regression test: if MCP_API_KEY is unset, API_KEY is None. A request sent
    with no x-api-key header also reads as None, so a naive `!=` comparison let
    it through. The server must reject every request while unconfigured instead."""
    monkeypatch.setattr(main, "API_KEY", None)
    client = TestClient(_protected_app())

    response = client.get("/")

    assert response.status_code == 401
