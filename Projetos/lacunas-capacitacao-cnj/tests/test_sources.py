from pipeline.common import ProjectPaths
from pipeline.sources import load_source_registry, validate_source_registry


def test_load_source_registry_returns_prioritized_entries() -> None:
    paths = ProjectPaths.discover()
    sources = load_source_registry(paths.config / "sources.yml")

    assert len(sources) >= 2
    assert any(source["name"] == "pesquisas-judiciarias-producao-interna" for source in sources)
    assert any(source["type"] == "normative_acts" for source in sources)
    assert sources[0]["priority"] in {"high", "medium"}


def test_validate_source_registry_rejects_missing_required_fields() -> None:
    invalid = [
        {"name": "broken", "url": "https://example.test", "section": ""},
    ]

    try:
        validate_source_registry(invalid)
    except ValueError as exc:
        assert "section" in str(exc)
    else:
        raise AssertionError("expected ValueError for invalid source entry")
