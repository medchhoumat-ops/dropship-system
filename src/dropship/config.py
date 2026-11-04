"""Settings, target markets and secret handling.

Secrets come ONLY from environment variables (optionally loaded from a local
``.env`` file that is git-ignored). Everything else lives in
``config/settings.toml``.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

SECRET_ENV_VARS = (
    "CJ_MCP_TOKEN",
    "AE_APP_KEY",
    "AE_APP_SECRET",
    "AE_ACCESS_TOKEN",
    "APIFY_TOKEN",
    "SEMRUSH_API_KEY",
    "SERPAPI_KEY",
)

EU_WAREHOUSES = ("FR", "DE", "ES", "IT", "NL", "BE", "PL", "CZ")


@dataclass(frozen=True)
class Market:
    code: str  # our code: US, UK, CA, FR, DE
    iso: str  # ISO-3166 alpha-2 used by suppliers (GB for the UK)
    name: str
    currency: str
    usd_rate: float  # 1 USD = x local currency (rough, for display only)
    semrush_db: str
    google_gl: str
    google_hl: str
    google_domain: str
    trends_geo: str
    amazon_domain: str
    language: str
    near_warehouses: tuple[str, ...]  # warehouse countries accepted besides `iso`

    @property
    def warehouse_countries(self) -> tuple[str, ...]:
        return (self.iso, *[c for c in self.near_warehouses if c != self.iso])


MARKETS: dict[str, Market] = {
    "US": Market("US", "US", "United States", "USD", 1.0, "us", "us", "en", "google.com",
                 "US", "amazon.com", "en", ("CA",)),
    "UK": Market("UK", "GB", "United Kingdom", "GBP", 0.79, "uk", "uk", "en", "google.co.uk",
                 "GB", "amazon.co.uk", "en", EU_WAREHOUSES),
    "CA": Market("CA", "CA", "Canada", "CAD", 1.37, "ca", "ca", "en", "google.ca",
                 "CA", "amazon.ca", "en", ("US",)),
    "FR": Market("FR", "FR", "France", "EUR", 0.92, "fr", "fr", "fr", "google.fr",
                 "FR", "amazon.fr", "fr", EU_WAREHOUSES),
    "DE": Market("DE", "DE", "Germany", "EUR", 0.92, "de", "de", "de", "google.de",
                 "DE", "amazon.de", "de", EU_WAREHOUSES),
}


def get_market(code: str) -> Market:
    key = code.strip().upper()
    if key == "GB":
        key = "UK"
    if key not in MARKETS:
        raise ValueError(f"Unsupported market {code!r}. Choose one of {', '.join(MARKETS)}")
    return MARKETS[key]


def load_dotenv(path: Path) -> None:
    """Minimal .env loader: KEY=VALUE lines, never overrides real env vars."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().removeprefix("export ").strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    data_dir: Path = Path("data")
    markets: list[str] = field(default_factory=lambda: ["US"])
    force_mock: bool = False
    cache_ttl_hours: float = 168
    # filters
    landed_min: float = 5.0
    landed_max: float = 15.0
    max_delivery_days: int = 10
    single_variant_only: bool = True
    # pricing
    multiplier_min: float = 4.0
    multiplier_max: float = 5.0
    fee_pct: float = 0.029
    fee_fixed: float = 0.30
    # research
    use_google_trends: bool = False
    amazon_max_items: int = 20
    shopping_max_items: int = 40
    # niche
    top_niches: int = 5
    min_ideas: int = 4
    max_ideas_per_niche: int = 8
    enrich_top: int = 10
    # competitors
    max_competitor_stores: int = 5
    apify_amazon_actor: str = "junglee~amazon-crawler"
    keys: dict[str, str] = field(default_factory=dict, repr=False)

    @property
    def cache_dir(self) -> Path:
        return self.data_dir / "cache"

    @property
    def runs_dir(self) -> Path:
        return self.data_dir / "runs"

    @property
    def reports_dir(self) -> Path:
        return self.data_dir.parent / "reports" if self.data_dir.name == "data" else self.data_dir / "reports"

    @property
    def default_market(self) -> Market:
        return get_market(self.markets[0])

    def key(self, name: str) -> str:
        return self.keys.get(name, "")

    def has_keys(self, *names: str) -> bool:
        return all(self.key(n) for n in names)


def load_settings(config_path: str | Path | None = None, *, mock: bool | None = None) -> Settings:
    load_dotenv(Path.cwd() / ".env")
    path = Path(config_path or os.environ.get("DROPSHIP_CONFIG", "config/settings.toml"))
    cfg: dict = {}
    if path.is_file():
        with path.open("rb") as fh:
            cfg = tomllib.load(fh)

    s = Settings()
    s.markets = [get_market(m).code for m in cfg.get("markets", s.markets)] or ["US"]
    s.cache_ttl_hours = float(cfg.get("cache", {}).get("ttl_hours", s.cache_ttl_hours))
    f = cfg.get("filters", {})
    s.landed_min = float(f.get("landed_min_usd", s.landed_min))
    s.landed_max = float(f.get("landed_max_usd", s.landed_max))
    s.max_delivery_days = int(f.get("max_delivery_days", s.max_delivery_days))
    s.single_variant_only = bool(f.get("single_variant_only", s.single_variant_only))
    p = cfg.get("pricing", {})
    s.multiplier_min = float(p.get("multiplier_min", s.multiplier_min))
    s.multiplier_max = float(p.get("multiplier_max", s.multiplier_max))
    s.fee_pct = float(p.get("fee_pct", s.fee_pct))
    s.fee_fixed = float(p.get("fee_fixed", s.fee_fixed))
    r = cfg.get("research", {})
    s.use_google_trends = bool(r.get("use_google_trends", s.use_google_trends))
    s.amazon_max_items = int(r.get("amazon_max_items", s.amazon_max_items))
    s.shopping_max_items = int(r.get("shopping_max_items", s.shopping_max_items))
    n = cfg.get("niche", {})
    s.top_niches = int(n.get("top_niches", s.top_niches))
    s.min_ideas = int(n.get("min_ideas", s.min_ideas))
    s.max_ideas_per_niche = int(n.get("max_ideas_per_niche", s.max_ideas_per_niche))
    s.enrich_top = int(n.get("enrich_top", s.enrich_top))
    s.max_competitor_stores = int(cfg.get("competitors", {}).get("max_stores", s.max_competitor_stores))

    s.data_dir = Path(os.environ.get("DROPSHIP_DATA_DIR", "data"))
    s.force_mock = _truthy(os.environ.get("DROPSHIP_MOCK")) if mock is None else mock
    s.keys = {name: os.environ.get(name, "").strip() for name in SECRET_ENV_VARS}
    s.apify_amazon_actor = os.environ.get("APIFY_AMAZON_ACTOR", "").strip() or s.apify_amazon_actor
    return s
