from pipeline.common import normalize_text, normalize_url, stable_id


def test_normalize_url_removes_fragment_and_sorts_query() -> None:
    url = "HTTPS://WWW.CNJ.JUS.BR/doc.pdf?b=2&a=1#pagina"
    assert normalize_url(url) == "https://www.cnj.jus.br/doc.pdf?a=1&b=2"


def test_normalize_text_removes_accents_and_case() -> None:
    assert normalize_text("  CAPACITAÇÃO  ") == "capacitacao"


def test_stable_id_is_deterministic() -> None:
    assert stable_id("doc", "url") == stable_id("doc", "url")
    assert stable_id("doc", "url") != stable_id("doc", "outra-url")
