import pytest

from dropship.config import SECRET_ENV_VARS, load_settings
from dropship.research import make_clients


@pytest.fixture(autouse=True)
def _isolated_env(tmp_path, monkeypatch):
    """No real keys, no network, data written to a temp dir."""
    for name in SECRET_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("DROPSHIP_MOCK", "1")
    monkeypatch.setenv("DROPSHIP_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.chdir(tmp_path)  # no stray .env / settings.toml


@pytest.fixture
def settings():
    return load_settings()


@pytest.fixture
def clients(settings):
    return make_clients(settings)
