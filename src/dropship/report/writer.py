"""Persist run documents (data/runs/*.json) and render HTML (data/reports/*.html)."""

from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from ..config import Settings


def _sparkline(values, width=120, height=28) -> str:
    vals = [float(v) for v in (values or []) if v is not None]
    if len(vals) < 2:
        return ""
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1
    step = width / (len(vals) - 1)
    pts = " ".join(f"{i * step:.1f},{height - 2 - (v - lo) / span * (height - 4):.1f}"
                   for i, v in enumerate(vals))
    return (f'<svg class="spark" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
            f'aria-hidden="true"><polyline fill="none" stroke="currentColor" stroke-width="2" '
            f'points="{pts}"/></svg>')


def _money(v, cur="$"):
    return "–" if v is None else f"{cur}{v:,.2f}"


def _pct(v, signed=False):
    if v is None:
        return "–"
    return f"{v * 100:+.0f}%" if signed else f"{v * 100:.0f}%"


def _env() -> Environment:
    env = Environment(loader=PackageLoader("dropship.report", "templates"),
                      autoescape=select_autoescape(["html", "j2"]), trim_blocks=True, lstrip_blocks=True)
    env.filters.update(money=_money, pct=_pct, sparkline=_sparkline,
                       num=lambda v: "–" if v is None else f"{v:,.0f}")
    return env


def render_html(run: dict) -> str:
    return _env().get_template("report.html.j2").render(run=run)


def save_run(run: dict, settings: Settings) -> tuple[Path, Path]:
    settings.runs_dir.mkdir(parents=True, exist_ok=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    json_path = settings.runs_dir / f"{run['id']}.json"
    json_path.write_text(json.dumps(run, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    html_path = settings.reports_dir / f"{run['id']}.html"
    html_path.write_text(render_html(run), encoding="utf-8")
    return json_path, html_path


def load_run(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def latest_run(settings: Settings) -> Path | None:
    runs = sorted(settings.runs_dir.glob("*.json")) if settings.runs_dir.is_dir() else []
    return runs[-1] if runs else None
