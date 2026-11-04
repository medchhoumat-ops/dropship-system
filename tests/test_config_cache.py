import json

import pytest

from dropship.cache import JsonCache
from dropship.config import get_market, load_settings
from dropship.http import BaseClient


def test_markets():
    assert get_market("uk").iso == "GB"
    assert get_market("GB").code == "UK"
    assert "DE" in get_market("FR").warehouse_countries
    with pytest.raises(ValueError):
        get_market("MA")


def test_settings_toml_and_env(tmp_path, monkeypatch):
    cfg = tmp_path / "s.toml"
    cfg.write_text('markets = ["DE", "FR"]\n[filters]\nmax_delivery_days = 7\n')
    monkeypatch.setenv("SEMRUSH_API_KEY", "secret-123")
    s = load_settings(cfg)
    assert s.markets == ["DE", "FR"]
    assert s.default_market.code == "DE"
    assert s.max_delivery_days == 7
    assert s.key("SEMRUSH_API_KEY") == "secret-123"
    assert "secret-123" not in repr(s)


def test_dotenv_does_not_override(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("SERPAPI_KEY=from-file\nAPIFY_TOKEN=tok\n")
    monkeypatch.setenv("SERPAPI_KEY", "from-env")
    s = load_settings()
    assert s.key("SERPAPI_KEY") == "from-env"
    assert s.key("APIFY_TOKEN") == "tok"


def test_cache_roundtrip_and_ttl(tmp_path):
    c = JsonCache(tmp_path, ttl_hours=1)
    assert c.get("x", "ep", {"a": 1}) is None
    path = c.set("x", "ep", {"a": 1}, {"ok": True})
    assert path.parent.name == "x"
    assert c.get("x", "ep", {"a": 1}) == {"ok": True}
    blob = json.loads(path.read_text())
    blob["fetched_at"] = 0
    path.write_text(json.dumps(blob))
    assert c.get("x", "ep", {"a": 1}) is None


class _Echo(BaseClient):
    source = "echo"


def test_secrets_never_cached(tmp_path, monkeypatch):
    import httpx

    seen = {}

    def handler(request):
        seen.update(request.url.params)
        return httpx.Response(200, json={"q": request.url.params.get("q")})

    s = load_settings(mock=False)
    client = _Echo(s, mock=False, http=httpx.Client(transport=httpx.MockTransport(handler)))
    data = client.call("ep", "https://example.test/api", {"q": "dog"}, secret_params={"key": "TOPSECRET"})
    assert seen["key"] == "TOPSECRET"  # sent to the API...
    files = list(s.cache_dir.rglob("*.json"))
    assert len(files) == 1
    assert "TOPSECRET" not in files[0].read_text()  # ...but never written to the cache
    assert json.loads(files[0].read_text())["params"]["params"] == {"q": "dog"}
    # second call is served from cache
    client._http = None
    assert client.call("ep", "https://example.test/api", {"q": "dog"}, secret_params={"key": "x"}) == data
