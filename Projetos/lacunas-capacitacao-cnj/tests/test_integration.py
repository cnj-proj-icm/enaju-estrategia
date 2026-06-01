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
    monkeypatch.setattr("pipeline.outputs._render_markdown_docx", lambda *args, **kwargs: False)
    outputs = build_outputs(context)
    assert outputs["status"] == "final"
