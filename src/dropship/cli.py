"""Command line interface: `dropship niche|research|source|report`."""

from __future__ import annotations

import logging
import webbrowser
from pathlib import Path

import typer

from .config import Settings, get_market, load_settings
from .pipeline import run_niche, run_research, run_source
from .report import latest_run, load_run, save_run
from .research import make_clients

app = typer.Typer(add_completion=False, no_args_is_help=True,
                  help="Product-research engine for a one-niche Shopify dropshipping store.")


class State:
    settings: Settings
    mock: bool | None = None


state = State()


@app.callback()
def main(
    mock: bool = typer.Option(False, "--mock", help="Force mock fixtures for every API."),
    config: Path | None = typer.Option(None, "--config", help="Path to settings.toml."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    logging.basicConfig(level=logging.INFO if verbose else logging.WARNING,
                        format="%(levelname)s %(message)s")
    state.settings = load_settings(config, mock=True if mock else None)
    state.mock = True if mock else None


def _market(country: str | None):
    try:
        return get_market(country) if country else state.settings.default_market
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


def _finish(run: dict) -> None:
    json_path, html_path = save_run(run, state.settings)
    mocked = [k for k, v in run["modes"].items() if v == "mock"]
    if mocked:
        typer.secho(f"note: mock data for {', '.join(mocked)}", fg=typer.colors.YELLOW)
    typer.echo(f"JSON:   {json_path}")
    typer.echo(f"Report: {html_path}")


def _print_picks(run: dict) -> None:
    if run["picks"]:
        typer.secho(f"\nPicks ({len(run['picks'])}):", bold=True)
        for i, e in enumerate(run["picks"], 1):
            pr, sh = e["pricing"], e["filter"]["shipping"]
            typer.echo(f" {i}. [{e['score']['total']:5.1f} {e['score']['grade']}] {e['product']['title'][:50]:50} "
                       f"{e['product']['platform']:10} landed ${pr['landed_cost']:.2f} -> ${pr['price']:.2f} "
                       f"margin {pr['margin_pct'] * 100:.0f}% BE-CPA ${pr['breakeven_cpa']:.2f} "
                       f"{sh['min_days']}-{sh['max_days']}d from {sh['from_country']}")
    if run["rejected"]:
        typer.secho(f"\nRejected ({len(run['rejected'])}):", bold=True)
        for e in run["rejected"][:10]:
            typer.echo(f" - {e['product']['title'][:50]:50} {'; '.join(e['filter']['failures'])}")


@app.command()
def niche(
    seeds: str = typer.Option(..., "--seeds", help='Comma-separated seed categories, e.g. "pets,kitchen".'),
    country: str | None = typer.Option(None, "--country", "-c", help="US, UK, CA, FR or DE."),
    source: bool = typer.Option(False, "--source", help="Also source the top niche's product ideas."),
) -> None:
    """Deep search: rank niches from seed categories; top 5 with 4+ product ideas each."""
    market = _market(country)
    seed_list = [s.strip() for s in seeds.split(",") if s.strip()]
    clients = make_clients(state.settings, state.mock)
    run = run_niche(seed_list, market, state.settings, clients, source=source)
    typer.secho(f"Top niches for {market.name}:", bold=True)
    for i, n in enumerate(run["niches"], 1):
        ideas = ", ".join(x["keyword"] for x in n["ideas"][:6])
        typer.echo(f" {i}. [{n['score']:5.1f}] {n['name']} ({n['category']}) – {n['demand']:,} searches/mo, "
                   f"trend {n['trend'] * 100:+.0f}%\n      ideas: {ideas}")
    if not run["niches"]:
        typer.secho("No niche had enough product ideas with search volume.", fg=typer.colors.RED)
    _print_picks(run)
    _finish(run)


@app.command()
def research(
    keyword: str = typer.Argument(..., help="Keyword to research."),
    country: str | None = typer.Option(None, "--country", "-c"),
    amazon: bool = typer.Option(True, "--amazon/--no-amazon", help="Run the Apify Amazon actor."),
    competitors: bool = typer.Option(True, "--competitors/--no-competitors"),
    competitor: list[str] = typer.Option([], "--competitor", help="Extra competitor domain(s) to inspect."),
) -> None:
    """Search volume, 12-month trend, Amazon and Google Shopping data for one keyword."""
    market = _market(country)
    clients = make_clients(state.settings, state.mock)
    run = run_research(keyword, market, state.settings, clients, amazon=amazon,
                       competitors=competitors, extra_domains=competitor)
    r = run["research"][0]
    typer.secho(f"{keyword!r} in {market.name}", bold=True)
    typer.echo(f" volume {r['volume']:,}/mo · CPC ${r['cpc']:.2f} · competition {r['competition']:.2f} · "
               f"trend {r['trend_change'] * 100:+.0f}% ({r['trend_source']})")
    if r.get("amazon"):
        a = r["amazon"]
        typer.echo(f" Amazon: {a['count']} results, median ${a['price_median']}, median reviews "
                   f"{a['reviews_median']}, best BSR {a['best_bsr']}, {a['sellers']} sellers")
    if r.get("shopping"):
        s = r["shopping"]
        typer.echo(f" Google Shopping: {s['count']} offers from {s['sellers']} sellers, "
                   f"${s['price_min']}–${s['price_max']} (median ${s['price_median']})")
    for s in run["competitors"]:
        typer.echo(f" store {s['domain']}: shopify={s['is_shopify']} theme={s['theme']} "
                   f"+{len(s['strengths'])}/-{len(s['gaps'])}")
    _finish(run)


@app.command()
def source(
    query: str = typer.Argument(..., help="Keyword, CJ pid (or cj:<pid>) or AliExpress id (or ae:<id>)."),
    country: str | None = typer.Option(None, "--country", "-c"),
    limit: int = typer.Option(5, "--limit", help="Products per platform for keyword searches."),
    keyword: str | None = typer.Option(None, "--keyword", help="Keyword for demand data when querying by id."),
    platform: str = typer.Option("all", "--platform", help="all, cj or aliexpress."),
    amazon: bool = typer.Option(True, "--amazon/--no-amazon"),
    competitors: bool = typer.Option(True, "--competitors/--no-competitors"),
) -> None:
    """Find suppliers, filter, price, score and write creatives for a product."""
    market = _market(country)
    platforms = ("cj", "aliexpress") if platform == "all" else (platform.lower(),)
    clients = make_clients(state.settings, state.mock)
    run = run_source(query, market, state.settings, clients, limit=limit, keyword=keyword,
                     platforms=platforms, amazon=amazon, competitors=competitors)
    _print_picks(run)
    if not run["picks"]:
        typer.secho("\nNo product passed the filters.", fg=typer.colors.RED)
    _finish(run)


@app.command()
def report(
    run: Path | None = typer.Option(None, "--run", help="Run JSON (default: latest in data/runs)."),
    open_browser: bool = typer.Option(False, "--open", help="Open the HTML report in a browser."),
) -> None:
    """(Re)build the HTML + JSON report for the latest run (or --run FILE)."""
    path = run or latest_run(state.settings)
    if not path or not Path(path).is_file():
        typer.secho("No runs yet. Run `dropship niche|research|source` first.", fg=typer.colors.RED)
        raise typer.Exit(1)
    doc = load_run(path)
    json_path, html_path = save_run(doc, state.settings)
    typer.echo(f"JSON:   {json_path}\nReport: {html_path}")
    if open_browser:
        webbrowser.open(html_path.resolve().as_uri())


if __name__ == "__main__":  # pragma: no cover
    app()
