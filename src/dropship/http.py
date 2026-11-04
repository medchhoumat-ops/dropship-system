"""Shared HTTP client base: caching, throttling, retries and mock mode.

Each API client subclasses :class:`BaseClient` and implements
``has_credentials`` and ``mock_response``. Secrets are passed separately
(``secret_params`` / ``headers``) so they never reach the cache key or the
cache files.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from importlib import resources
from typing import Any

import httpx

from .cache import JsonCache
from .config import Settings

log = logging.getLogger("dropship")

USER_AGENT = "dropship-system/0.1 (+product research)"

_throttle_lock = threading.Lock()
_last_call: dict[str, float] = {}


class ApiError(RuntimeError):
    pass


def load_fixture(name: str) -> Any:
    """Load a sample fixture shipped in ``dropship/fixtures``."""
    text = resources.files("dropship.fixtures").joinpath(name).read_text(encoding="utf-8")
    return json.loads(text) if name.endswith(".json") else text


class BaseClient:
    source = "base"
    min_interval = 0.0  # seconds between real calls (rate limit)
    timeout = 60.0
    max_retries = 3

    def __init__(self, settings: Settings, mock: bool | None = None,
                 http: httpx.Client | None = None) -> None:
        self.settings = settings
        if mock is None:
            mock = settings.force_mock or not self.has_credentials()
            if mock and not settings.force_mock:
                log.info("%s: no credentials found, using mock fixtures", self.source)
        self.mock = mock
        self.cache = JsonCache(settings.cache_dir, settings.cache_ttl_hours)
        self._http = http

    # --- to override -----------------------------------------------------
    def has_credentials(self) -> bool:
        return True

    def mock_response(self, endpoint: str, params: dict) -> Any:  # pragma: no cover
        raise NotImplementedError

    def check(self, endpoint: str, data: Any) -> None:
        """Raise ApiError if the payload is an API-level error."""

    # --- plumbing --------------------------------------------------------
    @property
    def http(self) -> httpx.Client:
        if self._http is None:
            self._http = httpx.Client(timeout=self.timeout, follow_redirects=True,
                                      headers={"User-Agent": USER_AGENT})
        return self._http

    def _throttle(self) -> None:
        if not self.min_interval:
            return
        with _throttle_lock:
            wait = _last_call.get(self.source, 0) + self.min_interval - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            _last_call[self.source] = time.monotonic()

    def call(
        self,
        endpoint: str,
        url: str,
        params: dict | None = None,
        *,
        method: str = "GET",
        json_body: Any = None,
        headers: dict | None = None,
        secret_params: dict | None = None,
        parse: str = "json",
        use_cache: bool = True,
    ) -> Any:
        params = {k: v for k, v in (params or {}).items() if v is not None}
        cache_params = {"params": params, "body": json_body}
        if self.mock:
            return self.mock_response(endpoint, {**params, **({"body": json_body} if json_body else {})})
        if use_cache:
            cached = self.cache.get(self.source, endpoint, cache_params)
            if cached is not None:
                return cached

        query = {**params, **(secret_params or {})}
        last_exc: Exception | None = None
        for attempt in range(self.max_retries):
            self._throttle()
            try:
                resp = self.http.request(method, url, params=query, json=json_body, headers=headers)
            except httpx.HTTPError as exc:
                last_exc = exc
                time.sleep(2 ** attempt)
                continue
            if resp.status_code in (429, 500, 502, 503, 504):
                last_exc = ApiError(f"{self.source} {endpoint}: HTTP {resp.status_code}")
                time.sleep(2 ** (attempt + 1))
                continue
            if resp.status_code >= 400:
                raise ApiError(f"{self.source} {endpoint}: HTTP {resp.status_code}: {resp.text[:300]}")
            data = resp.json() if parse == "json" else resp.text
            self.check(endpoint, data)
            if use_cache:
                self.cache.set(self.source, endpoint, cache_params, data)
            return data
        raise ApiError(f"{self.source} {endpoint}: failed after {self.max_retries} tries: {last_exc}")
