from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

from .common import RunContext, json_loads, read_csv, write_csv

LOGGER = logging.getLogger(__name__)


def _explode_axes(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame.assign(eixo=pd.Series(dtype="object"))
    rows: list[dict[str, Any]] = []
    source = "eixos_revisados" if "eixos_revisados" in frame.columns else "eixos"
    for row in frame.to_dict("records"):
        value = row.get(source)
        if source == "eixos_revisados" and not str(value or "").strip():
            value = row.get("eixos")
        axes = json_loads(value, [])
        if isinstance(axes, str):
            axes = [item.strip() for item in axes.split(";") if item.strip()]
        for axis in axes or ["nao_classificado"]:
            rows.append({**row, "eixo": axis})
    return pd.DataFrame(rows)


def _render_markdown_docx(markdown_path: Path, docx_path: Path) -> bool:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        LOGGER.warning("Pandoc ausente; DOCX nao foi gerado.")
        return False
    subprocess.run(
        [pandoc, str(markdown_path), "-o", str(docx_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return True


def build_outputs(context: RunContext) -> dict[str, Any]:
    confirmed_path = context.paths.processed / "evidencias_confirmadas.csv"
    preliminary = not confirmed_path.exists()
    source_path = (
        confirmed_path
        if confirmed_path.exists()
        else context.paths.processed / "trechos_candidatos.csv"
    )
    evidence = read_csv(source_path)
    corpus = read_csv(context.paths.processed / "corpus_documentos.csv")
    if preliminary:
        status_label = "PRELIMINAR - candidatos automaticos ainda sem revisao humana"
    else:
        status_label = "FINAL - evidencias humanas confirmadas"
    by_document = (
        evidence.groupby(["doc_id", "titulo", "ano", "secao_portal"], dropna=False)
        .agg(evidencias=("evidencia_id", "count"), score_maximo=("score", "max"))
        .reset_index()
        .sort_values(["evidencias", "score_maximo"], ascending=False)
    )
    exploded = _explode_axes(evidence)
    by_axis = (
        exploded.groupby(["secao_portal", "eixo", "tipo_gap"], dropna=False)
        .agg(evidencias=("evidencia_id", "count"), documentos=("doc_id", "nunique"))
        .reset_index()
        .sort_values(["evidencias", "documentos"], ascending=False)
    )
    executive_axes = (
        exploded.groupby(["secao_portal", "eixo"], dropna=False)
        .agg(evidencias=("evidencia_id", "count"), documentos=("doc_id", "nunique"))
        .reset_index()
        .sort_values(["evidencias", "documentos"], ascending=False)
    )
    write_csv(by_document, context.paths.outputs / "resumo_por_documento.csv")
    write_csv(by_axis, context.paths.outputs / "resumo_por_eixo.csv")
    validation = _validation_markdown(context, corpus, evidence, status_label, preliminary)
    executive = _executive_markdown(context, corpus, evidence, executive_axes, status_label, preliminary)
    validation_path = context.paths.outputs / "relatorio_validacao.md"
    executive_path = context.paths.outputs / "resumo_executivo.md"
    validation_path.write_text(validation, encoding="utf-8")
    executive_path.write_text(executive, encoding="utf-8")
    generated_docx = _render_markdown_docx(executive_path, context.paths.outputs / "resumo_executivo.docx")
    summary = {
        "status": "preliminar" if preliminary else "final",
        "documentos_corpus": len(corpus),
        "evidencias": len(evidence),
        "docx_gerado": generated_docx,
    }
    context.update_manifest("outputs", **summary)
    return summary


def _validation_markdown(
    context: RunContext,
    corpus: pd.DataFrame,
    evidence: pd.DataFrame,
    status_label: str,
    preliminary: bool,
) -> str:
    return f"""# Relatorio de Validacao

## Status

**{status_label}**

## Linha de base

- `run_id`: `{context.run_id}`
- data de corte editorial: `{context.as_of}`
- documentos no corpus processado: `{len(corpus)}`
- trechos {'candidatos' if preliminary else 'confirmados'}: `{len(evidence)}`

## Pendencias humanas

{'A fila `data/processed/fila_revisao.csv` deve ser preenchida, auditada e importada antes da publicacao institucional.' if preliminary else 'A fila revisada foi importada e os resumos usam somente evidencias confirmadas.'}

## Criterios de aceite

- snapshot e hash registrados em `data/processed/manifest_run.json`;
- PDFs, textos e segmentos rastreaveis por `doc_id`;
- classificacao automatica identificada pela versao dos criterios;
- resultados institucionais condicionados a revisao humana.
"""


def _executive_markdown(
    context: RunContext,
    corpus: pd.DataFrame,
    evidence: pd.DataFrame,
    by_axis: pd.DataFrame,
    status_label: str,
    preliminary: bool,
) -> str:
    axis_lines = "\n".join(
        f"- `{row['eixo']}`: {row['evidencias']} evidencias em {row['documentos']} documentos ({row['secao_portal']})"
        for row in by_axis.head(12).to_dict("records")
    ) or "- Nenhuma evidencia disponivel."
    return f"""# Sintese Executiva - Lacunas de Capacitacao em Producoes do CNJ

## Status

**{status_label}**

## Recorte

A linha de base `{context.run_id}` usa a fotografia editorial do portal de Pesquisas Judiciarias do CNJ em `{context.as_of}`. O corpus processado contem `{len(corpus)}` documentos e `{len(evidence)}` trechos {'candidatos' if preliminary else 'confirmados'}.

## Eixos em destaque

{axis_lines}

## Uso recomendado

{'Este documento organiza hipoteses para curadoria. Ele nao deve orientar decisoes institucionais antes da revisao humana.' if preliminary else 'Os achados confirmados apoiam a priorizacao de eixos e hipoteses de competencia. O primeiro ciclo nao propoe cursos ou trilhas formativas.'}

## Limites

- o corpus representa o portal e a data de corte, nao todo o Poder Judiciario;
- mencoes a capacitacao nao sao tratadas automaticamente como lacunas;
- hipoteses de competencia exigem validacao institucional antes de orientar oferta educacional.
"""
