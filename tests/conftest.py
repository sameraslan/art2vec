import pytest


@pytest.fixture(autouse=True)
def _cache_in_tmp(tmp_path, monkeypatch):
    """No test writes into the real user cache."""
    monkeypatch.setenv("ART2VEC_HOME", str(tmp_path / "art2vec-home"))
