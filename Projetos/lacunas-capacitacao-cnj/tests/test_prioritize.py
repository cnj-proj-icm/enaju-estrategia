from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

from pipeline.common import ProjectPaths, RunContext, write_csv
from pipeline.prioritize import import_calibration, prioritize_evidence


def _context(tmp_path: Path) -> RunContext:
    paths = ProjectPaths(tmp_path)
    paths.ensure()
    source_root = Path(__file__).resolve().parents[1]
    paths.config.mkdir(exist_ok=True)
    shutil.copyfile(
        source_root / "config" / "criterios_analiticos.yml",
        paths.config / "criterios_analiticos.yml",
    )
    return RunContext(paths=paths, run_id="fixture", as_of="2026-05-31")


def test_prioritize_calculates_deterministic_composite_score(tmp_path: Path) -> None:
    context = _context(tmp_path)
    write_csv(
        [
            {
                "evidencia_id": "ev_1",
                "doc_id": "doc_1",
                "titulo": "Relatorio DataJud",
                "ano": "2025",
                "url": "https://example.test/datajud.pdf",
                "secao_portal": "Producao Interna",
                "pagina": 1,
                "trecho": "necessidade de capacitacao para saneamento de dados",
                "eixos": '["dados_e_tecnologia"]',
                "tipo_gap": "explicito",
                "hipotese_competencia": "governanca e qualidade de dados",
                "score": 10,
            },
            {
                "evidencia_id": "ev_2",
                "doc_id": "doc_2",
                "titulo": "Nota sem classificacao",
                "ano": "2025",
                "url": "https://example.test/nota.pdf",
                "secao_portal": "Producao Interna",
                "pagina": 2,
                "trecho": "contexto generico",
                "eixos": '["nao_classificado"]',
                "tipo_gap": "potencial",
                "hipotese_competencia": "",
                "score": 1,
            },
        ],
        context.paths.processed / "trechos_candidatos.csv",
    )

    summary = prioritize_evidence(context)

    assert summary["evidencias_priorizadas"] == 2
    prioritized = pd.read_csv(context.paths.processed / "evidencias_priorizadas.csv", encoding="utf-8-sig")
    data_row = prioritized[prioritized["eixo"] == "dados_e_tecnologia"].iloc[0]
    unclassified = prioritized[prioritized["eixo"] == "nao_classificado"].iloc[0]
    assert data_row["score_final"] == 0.9875
    assert data_row["faixa_prioridade"] == "alta"
    assert unclassified["faixa_prioridade"] == "baixa"


def test_import_calibration_rejects_invalid_decision(tmp_path: Path) -> None:
    context = _context(tmp_path)
    review_file = context.paths.processed / "amostra_calibracao_preenchida.csv"
    write_csv(
        [
            {
                "tipo_amostra": "top_score",
                "evidencia_id": "ev_1",
                "decisao_calibracao": "decisao_invalida",
                "nota_calibracao": "",
            }
        ],
        review_file,
    )

    try:
        import_calibration(context, review_file)
    except ValueError as exc:
        assert "invalidas" in str(exc)
    else:
        raise AssertionError("expected invalid calibration decision to fail")


def test_import_calibration_writes_false_positive_rates(tmp_path: Path) -> None:
    context = _context(tmp_path)
    review_file = context.paths.processed / "amostra_calibracao_preenchida.csv"
    write_csv(
        [
            {
                "tipo_amostra": "top_score",
                "evidencia_id": "ev_1",
                "eixos": '["dados_e_tecnologia"]',
                "tipo_gap": "explicito",
                "score": 10,
                "decisao_calibracao": "falso_positivo",
                "nota_calibracao": "contexto nao formativo",
            },
            {
                "tipo_amostra": "top_score",
                "evidencia_id": "ev_2",
                "eixos": '["dados_e_tecnologia"]',
                "tipo_gap": "explicito",
                "score": 9,
                "decisao_calibracao": "gap_confirmado",
                "nota_calibracao": "",
            },
        ],
        review_file,
    )

    analysis = import_calibration(context, review_file)

    assert (context.paths.processed / "calibracao_analitica.csv").exists()
    assert analysis["revisados"].sum() == 2
    assert analysis["falsos_positivos"].sum() == 1
    high_score_row = analysis[analysis["score_faixa"] == "alto"].iloc[0]
    assert high_score_row["taxa_falso_positivo"] == 1.0
