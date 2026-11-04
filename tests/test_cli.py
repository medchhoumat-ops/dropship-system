import json

from typer.testing import CliRunner

from dropship.cli import app

runner = CliRunner()


def _ok(args):
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    return result.output


def test_research_command(tmp_path):
    out = _ok(["research", "dog lick mat", "--country", "US"])
    assert "volume" in out and "Report:" in out
    assert list((tmp_path / "data" / "reports").glob("*-research.html"))


def test_source_command_and_report(tmp_path):
    out = _ok(["source", "dog lick mat", "--country", "US"])
    assert "Picks" in out and "Rejected" in out
    run = json.loads(next((tmp_path / "data" / "runs").glob("*-source.json")).read_text())
    assert run["picks"], "mock data should produce at least one pick"
    for pick in run["picks"]:
        assert pick["filter"]["passed"]
        assert 5 <= pick["pricing"]["landed_cost"] <= 15
        assert pick["filter"]["shipping"]["max_days"] <= 10
        assert len(pick["product"]["variants"]) == 1
        assert len(pick["creative"]["image_prompts"]) == 4
        assert len(pick["creative"]["ugc_scripts"]) == 3
    html = next((tmp_path / "data" / "reports").glob("*-source.html")).read_text()
    assert "Why pick it" in html and "Competitor stores" in html
    out = _ok(["report"])
    assert "Report:" in out


def test_source_by_id(tmp_path):
    out = _ok(["source", "ae:1005006000000001", "--country", "UK", "--no-amazon"])
    assert "aliexpress" in out


def test_niche_command(tmp_path):
    out = _ok(["niche", "--country", "US", "--seeds", "pets,kitchen"])
    assert out.count("ideas:") == 5
    run = json.loads(next((tmp_path / "data" / "runs").glob("*-niche.json")).read_text())
    assert len(run["niches"]) == 5


def test_bad_country():
    result = runner.invoke(app, ["research", "x", "--country", "MA"])
    assert result.exit_code != 0


def test_report_without_runs():
    result = runner.invoke(app, ["report"])
    assert result.exit_code == 1
