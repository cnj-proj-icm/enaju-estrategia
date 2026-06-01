import pytest

from pipeline.corpus import _window_segments, clean_pages


def test_clean_pages_removes_repeated_margins_and_fixes_hyphenation() -> None:
    pages = [
        "CABECALHO\nlinha com gover-\nnanca de dados\nRODAPE 1",
        "CABECALHO\noutro texto\nRODAPE 2",
        "CABECALHO\nmais texto\nRODAPE 3",
    ]
    cleaned = clean_pages(pages)
    assert "CABECALHO" not in cleaned[0]
    assert "RODAPE" not in cleaned[0]
    assert "governanca" in cleaned[0]


def test_window_segments_overlap() -> None:
    segments = _window_segments("a" * 25, window=10, overlap=2)
    assert [(start, end) for start, end, _ in segments] == [(0, 10), (8, 18), (16, 25)]


def test_window_segments_rejects_no_text() -> None:
    assert _window_segments("", window=10, overlap=2) == []
