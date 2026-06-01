from pipeline.catalog import (
    _apply_relations_and_status,
    _assign_families,
    extract_editorial_cards,
)

HTML = b"""
<html><body>
  <a href="https://example.test/global.pdf">link global ignorado</a>
  <h2>Produ\xc3\xa7\xc3\xa3o Interna</h2>
  <section data-element_type="section" data-id="card-a">
    <a href="/wp-content/uploads/2025/01/relatorio-x-2025.pdf"><img /></a>
    <h4>Relat\xc3\xb3rio X 2025</h4>
    <a href="/wp-content/uploads/2025/01/sumario-relatorio-x-2025.pdf">Sum\xc3\xa1rio executivo</a>
    <a href="/wp-content/uploads/2025/01/justice-report-x-2025.pdf">Justice in Numbers 2025</a>
  </section>
  <h2>Parcerias Institucionais</h2>
  <section data-element_type="section" data-id="card-b">
    <h4>Diagn\xc3\xb3stico Y</h4>
    <a href="/wp-content/uploads/2024/02/diagnostico-y.pdf">Diagn\xc3\xb3stico completo</a>
  </section>
</body></html>
"""


def _records_from_cards():
    cards = extract_editorial_cards(HTML, "https://www.cnj.jus.br/pesquisas-judiciarias/")
    records = []
    for card in cards:
        for link in card.links:
            if link["tipo_recurso"] != "pdf":
                continue
            filename = link["url"].rsplit("/", 1)[-1]
            label = link["texto_ancora"]
            if "sumario" in filename:
                kind, language = "sumario", "pt"
            elif "justice" in filename:
                kind, language = "relatorio", "en"
            elif "diagnostico" in filename:
                kind, language = "diagnostico", "pt"
            else:
                kind, language = "relatorio", "pt"
            records.append(
                {
                    "doc_id": filename,
                    "titulo_inferido": card.title,
                    "ano_url": 2025 if "2025" in filename else 2024,
                    "ano_documento": 2025 if "2025" in filename else None,
                    "tipo_documento": kind,
                    "idioma_inferido": language,
                }
            )
    return cards, records


def test_cards_capture_links_before_and_after_heading_and_ignore_globals() -> None:
    cards, _ = _records_from_cards()
    assert [card.card_id for card in cards] == ["card-a", "card-b"]
    assert len(cards[0].links) == 3
    assert all("global.pdf" not in link["url"] for card in cards for link in card.links)


def test_relations_exclude_summary_and_translation() -> None:
    _, records = _records_from_cards()
    _assign_families(records, minimum_similarity=90)
    records, relations = _apply_relations_and_status(records, 2022, 2026)
    by_id = {row["doc_id"]: row for row in records}
    assert by_id["relatorio-x-2025.pdf"]["status_corpus"] == "incluir"
    assert by_id["sumario-relatorio-x-2025.pdf"]["status_corpus"] == "excluir"
    assert by_id["justice-report-x-2025.pdf"]["status_corpus"] == "excluir"
    assert {row["tipo_relacao"] for row in relations} == {"sumario_de", "traducao_de"}


def test_annual_reports_do_not_share_family() -> None:
    records = [
        {"titulo_inferido": "Relatorio Justica em Numeros 2024"},
        {"titulo_inferido": "Relatorio Justica em Numeros 2025"},
    ]
    _assign_families(records, minimum_similarity=90)
    assert records[0]["familia_documental_id"] != records[1]["familia_documental_id"]
