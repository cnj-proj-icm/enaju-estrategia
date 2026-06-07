from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd
import pymupdf

from pipeline.catalog import build_catalog
from pipeline.common import ProjectPaths, RunContext, sha256_bytes
from pipeline.corpus import build_corpus
from pipeline.detect import detect_candidates, import_review
from pipeline.outputs import build_outputs
from pipeline.prioritize import prioritize_evidence


class FakeResponse:
    def __init__(self, content: bytes, content_type: str = "application/pdf") -> None:
        self.content = content
        self.status_code = 200
        self.headers = {"content-type": content_type}

    def raise_for_status(self) -> None:
        return None


def _pdf_bytes() -> bytes:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Foi identificada necessidade de capacitacao para aprimorar o saneamento de dados no DataJud.",
    )
    content = document.tobytes()
    document.close()
    return content


def _context(tmp_path: Path) -> RunContext:
    paths = ProjectPaths(tmp_path)
    paths.ensure()
    source_root = Path(__file__).resolve().parents[1]
    paths.config.mkdir(exist_ok=True)
    shutil.copyfile(source_root / "config" / "pipeline.yml", paths.config / "pipeline.yml")
    shutil.copyfile(
        source_root / "config" / "criterios_analiticos.yml",
        paths.config / "criterios_analiticos.yml",
    )
    context = RunContext(paths=paths, run_id="fixture", as_of="2026-05-31")
    html = b"""
    <h2>Producao Interna</h2>
    <section data-element_type="section" data-id="fixture-card">
      <h4>Diagnostico DataJud 2025</h4>
      <a href="https://www.cnj.jus.br/wp-content/uploads/2025/01/diagnostico-datajud-2025.pdf">
        Relatorio completo
      </a>
    </section>
    """
    context.snapshot_html.write_bytes(html)
    context.snapshot_metadata.write_text(
        json.dumps({"snapshot_sha256": sha256_bytes(html)}),
        encoding="utf-8",
    )
    return context


def test_fixture_pipeline_generates_publishable_automated_report(monkeypatch, tmp_path: Path) -> None:
    context = _context(tmp_path)
    pdf = _pdf_bytes()
    monkeypatch.setattr("pipeline.corpus.requests.get", lambda *args, **kwargs: FakeResponse(pdf))
    build_catalog(context)
    build_corpus(context)
    detect_candidates(context)
    prioritize_evidence(context)

    def fake_docx(markdown_path: Path, docx_path: Path) -> bool:
        docx_path.write_text("fixture docx", encoding="utf-8")
        return True

    monkeypatch.setattr("pipeline.outputs._render_markdown_docx", fake_docx)

    outputs = build_outputs(context)

    assert outputs["status"] == "priorizado"
    report = (context.paths.outputs / "relatorio_publicavel.md").read_text(encoding="utf-8")
    assert "publicável" in report.lower()
    assert "alertas de risco" in report.lower()
    assert "automatiz" in report.lower()
    publication = (context.paths.outputs / "publicacao_final.md").read_text(encoding="utf-8")
    executive = (context.paths.outputs / "resumo_executivo.md").read_text(encoding="utf-8")
    assert "if preliminary else" not in publication
    assert "if preliminary else" not in executive
    assert "Evidências rastreáveis" in publication
    assert "Método utilizado e justificativa da escolha" in publication
    assert "Strings de busca para formação do corpus" in publication
    assert "Strings usadas na análise dos gaps" in publication
    assert "`necessidade de`" in publication
    assert "`capacitacao`" in publication
    assert "Portfólio preliminar para validação" in publication
    assert "score textual bruto utiliza escala própria" in publication
    assert "Plano proposto para análise robusta dos gaps" in publication
    assert "gap_observado" in publication
    assert "competencia_requerida" in publication
    assert "oferta_formativa" in publication
    assert (context.paths.outputs / "publicacao_final.docx").exists()
    assert (context.paths.outputs / "matriz_lacunas_priorizadas.csv").exists()
    assert (context.paths.outputs / "dossie_evidencias.csv").exists()


def test_fixture_pipeline_generates_csv_and_parquet(monkeypatch, tmp_path: Path) -> None:
    context = _context(tmp_path)
    pdf = _pdf_bytes()
    monkeypatch.setattr("pipeline.corpus.requests.get", lambda *args, **kwargs: FakeResponse(pdf))
    summary = build_catalog(context)
    assert summary["pdfs_incluir_provisorio"] == 1
    corpus_summary = build_corpus(context)
    assert corpus_summary["documentos_corpus"] == 1
    candidates = detect_candidates(context)
    assert len(candidates) >= 1
    csv_segments = pd.read_csv(context.paths.processed / "segmentos.csv", encoding="utf-8-sig")
    parquet_segments = pd.read_parquet(context.paths.processed / "segmentos.parquet")
    assert len(csv_segments) == len(parquet_segments)
    queue = pd.read_csv(context.paths.processed / "fila_revisao.csv", encoding="utf-8-sig")
    queue["decisao_revisor"] = "confirmado"
    queue["auditoria_status"] = "aprovado"
    queue["conciliacao_status"] = "nao_necessaria"
    queue_path = context.paths.processed / "fila_revisao_preenchida.csv"
    queue.to_csv(queue_path, index=False, encoding="utf-8-sig")
    confirmed = import_review(context, "data/processed/fila_revisao_preenchida.csv")
    assert len(confirmed) == len(queue)
    prioritize_evidence(context)
    monkeypatch.setattr("pipeline.outputs._render_markdown_docx", lambda *args, **kwargs: False)
    outputs = build_outputs(context)
    assert outputs["status"] == "priorizado"
