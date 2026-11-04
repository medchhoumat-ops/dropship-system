"""HTML + JSON report per run."""

from .writer import latest_run, load_run, render_html, save_run

__all__ = ["latest_run", "load_run", "render_html", "save_run"]
