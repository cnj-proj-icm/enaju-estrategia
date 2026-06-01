from __future__ import annotations

import json
from pathlib import Path

from pipeline.checklist import build_checklist
from pipeline.common import ProjectPaths, RunContext, write_csv


def _context(tmp_path: Path) -> RunContext:
    paths = ProjectPaths(tmp_path)
    paths.ensure()
    paths.config.mkdir(exist_ok=True)
    (paths.config / "criterios_analiticos.yml").write_text(
        "versao: 0.1.0\n",
        encoding="utf-8",
    )
    return RunContext(paths=paths, run_id="fixture-run", as_of="2026-05-31")


def test_build_checklist_embeds_queues_and_export_contract(tmp_path: Path) -> None:
    context = _context(tmp_path)
    context.manifest_path.write_text(
        json.dumps({"steps": {"snapshot": {"snapshot_sha256": "fixture-sha"}}}),
        encoding="utf-8",
    )
    write_csv(
        [
            {
                "doc_id": "doc_1",
                "titulo_inferido": "Relatorio DataJud",
                "status_corpus": "revisar",
                "motivo_status": "divergencia temporal",
            }
        ],
        context.paths.processed / "fila_curadoria_catalogo.csv",
    )
    write_csv(
        [
            {
                "evidencia_id": "ev_cal_1",
                "tipo_amostra": "top_score",
                "trecho": "necessidade de capacitacao",
                "decisao_calibracao": "",
            }
        ],
        context.paths.processed / "amostra_calibracao.csv",
    )
    write_csv(
        [
            {
                "evidencia_id": "ev_1",
                "titulo": "Relatorio DataJud",
                "trecho": "necessidade de capacitacao",
                "decisao_revisor": "pendente",
                "auditoria_status": "pendente",
                "conciliacao_status": "pendente",
            }
        ],
        context.paths.processed / "fila_revisao.csv",
    )

    output = build_checklist(context)
    html = output.read_text(encoding="utf-8")

    assert output == context.paths.outputs / "checklist_validacao.html"
    assert "Relatorio DataJud" in html
    assert "fixture-sha" in html
    assert "fila_curadoria_catalogo_preenchida.csv" in html
    assert "amostra_calibracao_preenchida.csv" in html
    assert "fila_revisao_preenchida.csv" in html
    assert "localStorage" in html
