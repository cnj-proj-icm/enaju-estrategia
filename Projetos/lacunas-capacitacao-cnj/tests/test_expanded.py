from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

from pipeline.common import ProjectPaths, RunContext, write_csv, write_parquet
from pipeline.detect import detect_candidates
from pipeline.expanded import build_expanded_corpus, classify_source_item, discover_sources
from pipeline.prioritize import prioritize_evidence


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200, content_type: str = "text/html") -> None:
        self.content = text.encode("utf-8")
        self.status_code = status_code
        self.headers = {"content-type": content_type}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, pages: dict[str, str]) -> None:
        self.pages = pages

    def get(self, url: str, **kwargs) -> FakeResponse:  # noqa: ARG002
        return FakeResponse(self.pages[url])


def _context(tmp_path: Path) -> RunContext:
    paths = ProjectPaths(tmp_path)
    paths.ensure()
    source_root = Path(__file__).resolve().parents[1]
    paths.config.mkdir(exist_ok=True)
    shutil.copyfile(source_root / "config" / "criterios_analiticos.yml", paths.config / "criterios_analiticos.yml")
    shutil.copyfile(source_root / "config" / "pipeline.yml", paths.config / "pipeline.yml")
    (paths.config / "sources.yml").write_text(
        """
sources:
  - name: programas-fixture
    url: https://www.cnj.jus.br/programas-fixture/
    section: Programas Fixture
    priority: high
    type: program
    description: Fonte de teste.
""",
        encoding="utf-8",
    )
    return RunContext(paths=paths, run_id="fixture-expanded", as_of="2026-05-31")


def test_classify_source_item_distinguishes_methodological_use() -> None:
    seed = {"name": "atos", "url": "https://www.cnj.jus.br/atos_normativos/", "section": "Atos", "type": "normative_acts"}

    normative = classify_source_item("https://atos.cnj.jus.br/files/resolucao_126.pdf", "Resolucao 126", seed)
    news = classify_source_item("https://www.cnj.jus.br/noticias/cnj-capacita-servidores/", "Noticia", {"type": "news"})
    course = classify_source_item("https://www.cnj.jus.br/capacitacao/", "Curso autoinstrucional", {"type": "training"})
    report = classify_source_item("https://www.cnj.jus.br/wp-content/relatorio.pdf", "Relatorio diagnostico", {"type": "publications"})

    assert normative["fonte_tipo"] == "ato_normativo"
    assert normative["uso_metodologico"] == "competencia_requerida"
    assert news["fonte_tipo"] == "noticia_cnj"
    assert float(news["peso_fonte"]) < float(report["peso_fonte"])
    assert course["uso_metodologico"] == "oferta_formativa"


def test_discover_sources_and_build_expanded_html_corpus(monkeypatch, tmp_path: Path) -> None:
    context = _context(tmp_path)
    pages = {
        "https://www.cnj.jus.br/programas-fixture/": """
        <html><body><main>
          <h1>Programa de Capacitação Fixture</h1>
          <p>Esta pagina apresenta relatorio, manual e noticias sobre necessidade de capacitacao.</p>
          <p>O programa descreve dificuldades de implementacao, desafios de gestao, necessidades formativas, competencias requeridas e lacunas de planejamento para tribunais.</p>
          <p>O texto e propositalmente longo para representar uma pagina institucional analisavel pelo corpus expandido.</p>
          <a href="https://atos.cnj.jus.br/files/resolucao_126_2011.pdf">Resolução de formação</a>
          <a href="https://bibliotecadigital.cnj.jus.br/bitstream/123/1/guia-competencias.pdf">Guia de Gestão por Competências</a>
          <a href="https://www.cnj.jus.br/noticias/capacitacao-fixture/">Notícia de capacitação</a>
          <a href="https://paineisanalytics.cnj.jus.br/single/?appid=fixture">Painel</a>
        </main></body></html>
        """,
        "https://www.cnj.jus.br/noticias/capacitacao-fixture/": """
        <html><body><article>
          <h1>CNJ anuncia capacitação para tribunais</h1>
          <p>A notícia descreve curso, público-alvo e necessidade de implementação de política pública.</p>
          <p>O conteúdo é contextual e deve ter menor força probatória que diagnóstico ou relatório.</p>
          <p>Tambem registra treinamento, competencias esperadas, desafios de implantacao e demanda de acompanhamento pelos tribunais.</p>
        </article></body></html>
        """,
    }
    monkeypatch.setattr("pipeline.expanded.requests.Session", lambda: FakeSession(pages))

    summary = discover_sources(context, force=True)
    corpus_summary = build_expanded_corpus(context)

    catalog = pd.read_csv(context.paths.processed / "catalogo_fontes_expandido.csv", encoding="utf-8-sig")
    corpus = pd.read_csv(context.paths.processed / "corpus_documentos_expandido.csv", encoding="utf-8-sig")
    assert summary["itens_catalogados"] >= 4
    assert "ato_normativo" in set(catalog["fonte_tipo"])
    assert "manual_guia_cartilha" in set(catalog["fonte_tipo"])
    assert "noticia_cnj" in set(catalog["fonte_tipo"])
    assert corpus_summary["documentos_html_expandido"] >= 1
    assert (context.paths.processed / "segmentos_expandido.parquet").exists()
    assert "fonte_tipo" in corpus.columns


def test_expanded_detection_and_prioritization_generate_source_matrices(tmp_path: Path) -> None:
    context = _context(tmp_path)
    write_csv(
        [
            {
                "run_id": "fixture-expanded",
                "as_of": "2026-05-31",
                "snapshot_sha256": "sha",
                "doc_id": "doc_report",
                "titulo": "Relatorio de diagnostico",
                "ano": "2025",
                "url": "https://www.cnj.jus.br/relatorio.pdf",
                "secao_portal": "Publicacoes",
                "prioridade_analitica": "nucleo_expandido",
                "fonte_tipo": "relatorio_diagnostico_pesquisa",
                "peso_fonte": 1.0,
                "forca_probatoria": "alta",
                "uso_metodologico": "gap_observado",
            },
            {
                "run_id": "fixture-expanded",
                "as_of": "2026-05-31",
                "snapshot_sha256": "sha",
                "doc_id": "doc_course",
                "titulo": "Curso de capacitacao",
                "ano": "2025",
                "url": "https://www.cnj.jus.br/capacitacao/",
                "secao_portal": "Capacitacao",
                "prioridade_analitica": "contextual_expandido",
                "fonte_tipo": "oferta_formativa",
                "peso_fonte": 0.4,
                "forca_probatoria": "oferta",
                "uso_metodologico": "oferta_formativa",
            },
        ],
        context.paths.processed / "corpus_documentos_expandido.csv",
    )
    write_parquet(
        [
            {
                "segmento_id": "seg_1",
                "doc_id": "doc_report",
                "pagina": 1,
                "tipo_segmento": "janela",
                "char_inicio": 0,
                "char_fim": 120,
                "trecho": "Ha necessidade de capacitacao para aprimorar o saneamento de dados no DataJud.",
            },
            {
                "segmento_id": "seg_2",
                "doc_id": "doc_course",
                "pagina": 1,
                "tipo_segmento": "janela",
                "char_inicio": 0,
                "char_fim": 120,
                "trecho": "Curso autoinstrucional com carga horaria e certificacao para servidores.",
            },
        ],
        context.paths.processed / "segmentos_expandido.parquet",
    )

    candidates = detect_candidates(context)
    prioritize_evidence(context)

    assert "fonte_tipo" in candidates.columns
    assert "oferta_formativa" in set(candidates["achado_classe"])
    by_source = pd.read_csv(context.paths.outputs / "matriz_lacunas_por_tipo_fonte.csv", encoding="utf-8-sig")
    offer_gap = pd.read_csv(context.paths.outputs / "mapa_oferta_vs_lacuna.csv", encoding="utf-8-sig")
    assert "oferta_formativa" in set(by_source["achado_classe"])
    assert (offer_gap["ofertas_formativas"] > 0).any()
