"""Semrush Analytics API: keyword volume, CPC, competition, 12-month trend."""

from __future__ import annotations

from ..config import Market
from ..http import ApiError, BaseClient, load_fixture
from ..models import KeywordMetrics
from ..utils import seeded_rng, to_float

HEADER_MAP = {
    "keyword": "keyword",
    "search volume": "volume",
    "cpc": "cpc",
    "competition": "competition",
    "number of results": "results",
    "trends": "trend",
}

MOCK_MODIFIERS = [
    "best", "for small dogs", "portable", "set", "large", "for cats", "stainless steel",
    "silicone", "with timer", "for travel", "for kids", "rechargeable", "foldable", "anti slip",
    "amazon", "how to use", "diy",
]


def parse_semrush_csv(text: str) -> list[KeywordMetrics]:
    """Parse Semrush's semicolon-separated export. 'ERROR 50 :: NOTHING FOUND' -> []."""
    text = (text or "").strip()
    if not text or text.upper().startswith("ERROR"):
        return []
    lines = text.splitlines()
    header = [HEADER_MAP.get(h.strip().lower(), h.strip().lower()) for h in lines[0].split(";")]
    rows: list[KeywordMetrics] = []
    for line in lines[1:]:
        cols = dict(zip(header, line.split(";"), strict=False))
        if not cols.get("keyword"):
            continue
        trend = [float(t) for t in cols.get("trend", "").split(",") if t.strip()]
        rows.append(KeywordMetrics(
            keyword=cols["keyword"].strip(),
            volume=int(to_float(cols.get("volume"), 0) or 0),
            cpc=to_float(cols.get("cpc"), 0.0) or 0.0,
            competition=to_float(cols.get("competition"), 0.0) or 0.0,
            results=int(to_float(cols.get("results"), 0) or 0),
            trend=trend,
        ))
    return rows


def _mock_metrics(keyword: str, db: str) -> tuple[int, float, float, int, list[float]]:
    rng = seeded_rng("semrush", keyword, db)
    volume = int(rng.choice([480, 880, 1300, 2400, 3600, 5400, 8100, 12100, 18100, 27100]))
    cpc = round(rng.uniform(0.35, 2.4), 2)
    comp = round(rng.uniform(0.2, 1.0), 2)
    slope = rng.uniform(-0.04, 0.07)
    base = rng.uniform(0.45, 0.75)
    trend = [round(max(0.05, min(1.0, base * (1 + slope * i) + rng.uniform(-0.05, 0.05))), 2)
             for i in range(12)]
    peak = max(trend)
    trend = [round(t / peak, 2) for t in trend]
    return volume, cpc, comp, volume * rng.randint(900, 4000), trend


class SemrushClient(BaseClient):
    source = "semrush"
    URL = "https://api.semrush.com/"
    min_interval = 0.12  # Semrush allows ~10 req/s

    def has_credentials(self) -> bool:
        return self.settings.has_keys("SEMRUSH_API_KEY")

    def check(self, endpoint, data):
        if isinstance(data, str) and data.startswith("ERROR") and "NOTHING FOUND" not in data:
            raise ApiError(f"semrush: {data.strip()[:200]}")

    def _get(self, report: str, params: dict) -> str:
        return self.call(report, self.URL, {"type": report, **params}, parse="text",
                         secret_params={"key": self.settings.key("SEMRUSH_API_KEY")})

    def keyword_overview(self, keyword: str, market: Market) -> KeywordMetrics | None:
        text = self._get("phrase_this", {
            "phrase": keyword, "database": market.semrush_db,
            "export_columns": "Ph,Nq,Cp,Co,Nr,Td",
        })
        rows = parse_semrush_csv(text)
        return rows[0] if rows else None

    def related(self, keyword: str, market: Market, limit: int = 20) -> list[KeywordMetrics]:
        text = self._get("phrase_related", {
            "phrase": keyword, "database": market.semrush_db, "display_limit": limit,
            "export_columns": "Ph,Nq,Cp,Co,Td", "display_sort": "nq_desc",
        })
        return parse_semrush_csv(text)

    # ------------------------------------------------------------------ mock
    def mock_response(self, endpoint, params):
        kw, db = params.get("phrase", ""), params.get("database", "us")
        if endpoint == "phrase_this":
            vol, cpc, comp, res, trend = _mock_metrics(kw, db)
            return load_fixture("semrush_phrase_this.txt").format(
                keyword=kw, volume=vol, cpc=cpc, competition=comp, results=res,
                trends=",".join(map(str, trend)))
        if endpoint == "phrase_related":
            rng = seeded_rng("related", kw, db)
            mods = rng.sample(MOCK_MODIFIERS, k=min(int(params.get("display_limit", 10)), 10))
            rows = []
            for m in mods:
                phrase = f"{m} {kw}" if m in {"best", "portable", "large", "silicone", "foldable",
                                                "rechargeable", "stainless steel", "anti slip"} \
                    else f"{kw} {m}"
                vol, cpc, comp, _res, trend = _mock_metrics(phrase, db)
                rows.append(f"{phrase};{vol // 3};{cpc};{comp};{','.join(map(str, trend))}")
            return load_fixture("semrush_phrase_related.txt").format(rows="\n".join(rows))
        raise KeyError(endpoint)
