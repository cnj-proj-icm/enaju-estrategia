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
    if "eixo" in frame.columns:
        return frame.copy()
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
        LOGGER.warning("Pandoc ausente; DOCX nao foi gerado: %s", docx_path)
        return False
    try:
        subprocess.run(
            [pandoc, str(markdown_path), "-o", str(docx_path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        LOGGER.warning("Falha ao gerar DOCX %s: %s", docx_path, exc.stderr)
        return False
    return True


def _numeric_series(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        return pd.Series([0])
    return pd.to_numeric(frame[column], errors="coerce").fillna(0)


def _risk_alerts(evidence: pd.DataFrame) -> list[str]:
    alerts: list[str] = []
    if evidence.empty:
        return ["Nenhuma evidencia automatica foi detectada para este recorte."]

    base = evidence.drop_duplicates("evidencia_id").copy() if "evidencia_id" in evidence.columns else evidence
    scores = _numeric_series(base, "score")
    low_confidence = int((scores < 3).sum())
    if low_confidence:
        alerts.append(
            f"{low_confidence} trechos apresentam score textual baixo (< 3); devem ser lidos como hipoteses tecnicas."
        )

    if {"doc_id", "trecho"}.issubset(base.columns):
        duplicate_pairs = int(base.duplicated(subset=["doc_id", "trecho"]).sum())
        if duplicate_pairs:
            alerts.append(
                f"{duplicate_pairs} evidencias repetem o mesmo documento e trecho; a sintese consolida a mensagem para reduzir duplicidade."
            )

    if "tipo_gap" in base.columns:
        potential = int((base["tipo_gap"] == "potencial").sum())
        if potential:
            alerts.append(
                f"{potential} evidencias foram classificadas como potenciais; elas apoiam recomendacoes, mas nao constituem conclusoes institucionais isoladas."
            )

    if "taxa_falso_positivo_estimada" in evidence.columns:
        known_rates = pd.to_numeric(evidence["taxa_falso_positivo_estimada"], errors="coerce").dropna()
        if not known_rates.empty:
            alerts.append(
                f"A maior taxa de falso positivo estimada na calibracao amostral foi {known_rates.max():.1%}."
            )
    return alerts


def _source_path(context: RunContext) -> tuple[Path, str, bool]:
    prioritized = context.paths.processed / "evidencias_priorizadas.csv"
    if prioritized.exists():
        return prioritized, "evidencias_priorizadas", True
    confirmed = context.paths.processed / "evidencias_confirmadas.csv"
    if confirmed.exists():
        return confirmed, "evidencias_confirmadas", False
    return context.paths.processed / "trechos_candidatos.csv", "trechos_candidatos", False


def _calibration_summary(context: RunContext) -> dict[str, Any]:
    path = context.paths.processed / "calibracao_analitica.csv"
    import_step = context.load_manifest().get("steps", {}).get("import-calibration", {})
    if not path.exists():
        return {
            "status": "amostra_estruturada_sem_importacao",
            "descricao": "A amostra de calibracao foi gerada, mas ainda nao ha CSV preenchido importado.",
            "revisados": 0,
            "pendentes": "",
            "taxa_falso_positivo": "",
        }
    calibration = read_csv(path)
    reviewed = int(pd.to_numeric(calibration.get("revisados", pd.Series([0])), errors="coerce").fillna(0).sum())
    pending = int(pd.to_numeric(calibration.get("pendentes", pd.Series([0])), errors="coerce").fillna(0).sum())
    false_positive = int(
        pd.to_numeric(calibration.get("falsos_positivos", pd.Series([0])), errors="coerce").fillna(0).sum()
    )
    if import_step:
        reviewed = int(import_step.get("revisados", reviewed))
        pending = int(import_step.get("pendentes", pending))
    rate = round(false_positive / reviewed, 4) if reviewed else ""
    if reviewed:
        description = f"Calibracao amostral importada, com {reviewed} decisoes revisadas nos grupos analiticos."
        status = "calibracao_amostral_importada"
    else:
        description = "Arquivo de calibracao analitica existe, mas nao contem decisoes revisadas."
        status = "calibracao_sem_decisoes"
    return {
        "status": status,
        "descricao": description,
        "revisados": reviewed,
        "pendentes": pending,
        "taxa_falso_positivo": rate,
    }


def _status_label(prioritized: bool, calibration: dict[str, Any]) -> str:
    if prioritized and calibration["revisados"]:
        return "PROPOSTA TECNICA - priorizacao automatizada com calibracao amostral"
    if prioritized:
        return "PROPOSTA TECNICA - priorizacao automatizada com amostra de calibracao estruturada"
    return "PROPOSTA TECNICA - candidatos automatizados ainda sem matriz de priorizacao"


def _evidence_count(evidence: pd.DataFrame) -> int:
    if "evidencia_id" in evidence.columns:
        return int(evidence["evidencia_id"].nunique())
    return len(evidence)


def _evidence_axis_note(evidence: pd.DataFrame) -> str:
    unique = _evidence_count(evidence)
    if len(evidence) == unique:
        return f"{unique}"
    return f"{unique} evidencias unicas em {len(evidence)} linhas evidencia-eixo"


def _read_optional_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def build_outputs(context: RunContext) -> dict[str, Any]:
    source_path, source_label, prioritized = _source_path(context)
    evidence = read_csv(source_path)
    corpus_path = context.paths.processed / "corpus_documentos_expandido.csv"
    if not corpus_path.exists():
        corpus_path = context.paths.processed / "corpus_documentos.csv"
    corpus = read_csv(corpus_path)
    calibration = _calibration_summary(context)
    status_label = _status_label(prioritized, calibration)

    by_document = (
        evidence.groupby(["doc_id", "titulo", "ano", "secao_portal"], dropna=False)
        .agg(evidencias=("evidencia_id", "count"), score_maximo=("score", "max"))
        .reset_index()
        .sort_values(["evidencias", "score_maximo"], ascending=False)
    )
    if "score_final" in evidence.columns:
        score_final = (
            evidence.groupby("doc_id", dropna=False)
            .agg(score_final_maximo=("score_final", "max"))
            .reset_index()
        )
        by_document = by_document.merge(score_final, on="doc_id", how="left")

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

    matrix = _read_optional_csv(context.paths.outputs / "matriz_lacunas_priorizadas.csv")
    dossier = _read_optional_csv(context.paths.outputs / "dossie_evidencias.csv")
    portfolio = _read_optional_csv(context.paths.outputs / "trilhas_capacitacoes_evidencias.csv")
    source_matrix = _read_optional_csv(context.paths.outputs / "matriz_lacunas_por_tipo_fonte.csv")
    normative_matrix = _read_optional_csv(context.paths.outputs / "matriz_normativos_competencias.csv")
    offer_gap = _read_optional_csv(context.paths.outputs / "mapa_oferta_vs_lacuna.csv")

    validation = _validation_markdown(context, corpus, evidence, status_label, calibration, source_label)
    executive = _executive_markdown(context, corpus, evidence, executive_axes, matrix, status_label)
    publishable = _publishable_markdown(context, corpus, evidence, by_axis, matrix, status_label, calibration)
    publication = _publication_markdown(
        context,
        corpus,
        evidence,
        matrix,
        dossier,
        portfolio,
        source_matrix,
        normative_matrix,
        offer_gap,
        status_label,
        calibration,
    )
    portfolio_doc = _portfolio_markdown(context, portfolio, matrix, status_label)

    validation_path = context.paths.outputs / "relatorio_validacao.md"
    executive_path = context.paths.outputs / "resumo_executivo.md"
    publishable_path = context.paths.outputs / "relatorio_publicavel.md"
    publication_path = context.paths.outputs / "publicacao_final.md"
    portfolio_path = context.paths.outputs / "portfolio_publicacao.md"
    validation_path.write_text(validation, encoding="utf-8")
    executive_path.write_text(executive, encoding="utf-8")
    publishable_path.write_text(publishable, encoding="utf-8")
    publication_path.write_text(publication, encoding="utf-8")
    portfolio_path.write_text(portfolio_doc, encoding="utf-8")

    generated_executive_docx = _render_markdown_docx(executive_path, context.paths.outputs / "resumo_executivo.docx")
    generated_publication_docx = _render_markdown_docx(publication_path, context.paths.outputs / "publicacao_final.docx")
    summary = {
        "status": "priorizado" if prioritized else "preliminar",
        "fonte": source_label,
        "documentos_corpus": len(corpus),
        "corpus_expandido": str(corpus_path.name == "corpus_documentos_expandido.csv"),
        "evidencias": _evidence_count(evidence),
        "linhas_evidencia_eixo": len(evidence),
        "lacunas_priorizadas": len(matrix),
        "docx_resumo_gerado": generated_executive_docx,
        "docx_publicacao_gerado": generated_publication_docx,
    }
    context.update_manifest("outputs", **summary)
    return summary


def _markdown_table(frame: pd.DataFrame, columns: list[tuple[str, str]], limit: int | None = None) -> str:
    if frame.empty:
        return "_Nao ha registros disponiveis._"
    records = frame.head(limit).to_dict("records") if limit else frame.to_dict("records")
    header = "| " + " | ".join(label for _, label in columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    rows = []
    for record in records:
        values = []
        for key, _ in columns:
            value = str(record.get(key, ""))
            values.append(value.replace("|", "\\|").replace("\n", " "))
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join([header, sep, *rows])


def _axis_lines(by_axis: pd.DataFrame, limit: int = 10) -> str:
    return "\n".join(
        f"- `{row['eixo']}`: {row['evidencias']} evidencias em {row['documentos']} documentos ({row['secao_portal']})"
        for row in by_axis.head(limit).to_dict("records")
    ) or "- Nenhuma evidencia disponivel."


def _matrix_lines(matrix: pd.DataFrame, limit: int = 8) -> str:
    if matrix.empty:
        return "- Matriz de lacunas priorizadas ainda nao gerada."
    return "\n".join(
        f"- {row['proposta']}: score final `{row['score_final']}`, faixa `{row['faixa_prioridade']}`, "
        f"{row['evidencias_total']} evidencias em {row['documentos_impactados']} documentos."
        for row in matrix.head(limit).to_dict("records")
    )


def _alerts_markdown(evidence: pd.DataFrame) -> str:
    return "\n".join(f"- {alert}" for alert in _risk_alerts(evidence))


def _validation_markdown(
    context: RunContext,
    corpus: pd.DataFrame,
    evidence: pd.DataFrame,
    status_label: str,
    calibration: dict[str, Any],
    source_label: str,
) -> str:
    return f"""# Relatorio de Validacao

## Status

**{status_label}**

## Linha de base

- `run_id`: `{context.run_id}`
- data de corte editorial: `{context.as_of}`
- fonte analitica usada nos outputs: `{source_label}`
- documentos no corpus processado: `{len(corpus)}`
- evidencias consideradas: `{_evidence_axis_note(evidence)}`

## Calibracao amostral

{calibration['descricao']}

- decisoes revisadas: `{calibration['revisados']}`
- pendencias registradas: `{calibration['pendentes']}`
- taxa de falso positivo estimada: `{calibration['taxa_falso_positivo']}`

## Alertas de risco

{_alerts_markdown(evidence)}

## Criterios de aceite

- snapshot e hash registrados em `data/processed/manifest_run.json`;
- PDFs, textos e segmentos rastreaveis por `doc_id`;
- classificacao automatica identificada pela versao dos criterios;
- score composto documentado em `config/criterios_analiticos.yml`;
- resultados apresentados como proposta tecnica, nao como deliberacao institucional final.
"""


def _executive_markdown(
    context: RunContext,
    corpus: pd.DataFrame,
    evidence: pd.DataFrame,
    by_axis: pd.DataFrame,
    matrix: pd.DataFrame,
    status_label: str,
) -> str:
    return f"""# Sintese Executiva - Lacunas de Capacitacao em Producoes do CNJ

## Status

**{status_label}**

## Recorte

A linha de base `{context.run_id}` usa a fotografia editorial do portal de Pesquisas Judiciarias do CNJ em `{context.as_of}`. O corpus processado contem `{len(corpus)}` documentos e {_evidence_axis_note(evidence)} consideradas.

## Lacunas e trilhas priorizadas

{_matrix_lines(matrix, limit=8)}

## Eixos em destaque

{_axis_lines(by_axis, limit=12)}

## Uso recomendado

Este documento e uma proposta tecnica baseada em evidencias automatizadas, matriz de priorizacao e calibracao amostral quando importada. Ele apoia decisao pedagogica e planejamento, mas nao substitui validacao institucional final.

## Limites

- o corpus representa o portal e a data de corte, nao todo o Poder Judiciario;
- mencoes a capacitacao nao sao tratadas automaticamente como lacunas;
- hipoteses de competencia exigem validacao institucional antes de orientar oferta educacional definitiva.
"""


def _publishable_markdown(
    context: RunContext,
    corpus: pd.DataFrame,
    evidence: pd.DataFrame,
    by_axis: pd.DataFrame,
    matrix: pd.DataFrame,
    status_label: str,
    calibration: dict[str, Any],
) -> str:
    scores = _numeric_series(evidence, "score")
    final_scores = _numeric_series(evidence, "score_final") if "score_final" in evidence.columns else pd.Series([0])
    return f"""# Relatorio Automatizado Publicavel - ENAJU/CNJ

## Status executivo

**{status_label}**

Este produto organiza uma proposta tecnica de priorizacao de lacunas de capacitacao com base em evidencias documentais rastreaveis, score composto e alertas de risco. A leitura correta e de apoio a decisao, sem substituir a deliberacao institucional da ENAJU ou das escolas judiciais.

## Resumo operacional

- run_id: `{context.run_id}`
- data de corte editorial: `{context.as_of}`
- documentos no corpus: `{len(corpus)}`
- evidencias consideradas: `{_evidence_axis_note(evidence)}`
- score textual medio: `{round(float(scores.mean()), 2) if not evidence.empty else 0.0}`
- score final medio: `{round(float(final_scores.mean()), 4) if "score_final" in evidence.columns else "nao gerado"}`
- calibracao: `{calibration['status']}`

## Lacunas priorizadas

{_matrix_lines(matrix, limit=10)}

## Eixos documentais

{_axis_lines(by_axis, limit=10)}

## Alertas de risco

{_alerts_markdown(evidence)}

## Recomendacao de uso

- Usar como proposta tecnica para planejamento de capacitacoes e trilhas.
- Cruzar os achados com prioridades pedagogicas, capacidade operacional e agenda institucional.
- Registrar qualquer decisao final em ata, parecer ou documento institucional proprio.
"""


def _publication_markdown(
    context: RunContext,
    corpus: pd.DataFrame,
    evidence: pd.DataFrame,
    matrix: pd.DataFrame,
    dossier: pd.DataFrame,
    portfolio: pd.DataFrame,
    source_matrix: pd.DataFrame,
    normative_matrix: pd.DataFrame,
    offer_gap: pd.DataFrame,
    status_label: str,
    calibration: dict[str, Any],
) -> str:
    matrix_table = _markdown_table(
        matrix,
        [
            ("faixa_prioridade", "Faixa"),
            ("proposta", "Proposta"),
            ("evidencias_total", "Evidencias"),
            ("documentos_impactados", "Documentos"),
            ("score_final", "Score final"),
        ],
        limit=10,
    )
    portfolio_table = _markdown_table(
        portfolio,
        [
            ("faixa_prioridade", "Prioridade"),
            ("proposta", "Proposta"),
            ("publico_prioritario", "Publico prioritario"),
            ("carga_horaria_sugerida", "Carga horaria"),
            ("modalidade_sugerida", "Modalidade"),
        ],
        limit=10,
    )
    dossier_table = _markdown_table(
        dossier,
        [
            ("proposta", "Proposta"),
            ("titulo", "Documento"),
            ("pagina", "Pagina"),
            ("score_final", "Score final"),
            ("trecho_curto", "Evidencia rastreavel"),
        ],
        limit=18,
    )
    expansion_section = _expansion_section(corpus, source_matrix, normative_matrix, offer_gap)
    return f"""# Modelo de priorizacao de capacitacoes para escolas judiciais a partir de evidencias documentais do CNJ

## 1. Resumo executivo

Este documento apresenta uma proposta tecnica para identificar lacunas de capacitacao em producoes do CNJ e converte-las em um portfolio inicial de trilhas e capacitacoes. O produto combina coleta documental, identificacao automatizada de evidencias, score composto, matriz de priorizacao e alertas de risco.

**Status da entrega:** {status_label}.

## 2. Corpus e alcance

A linha de base `{context.run_id}` considera a fotografia editorial de `{context.as_of}` do portal de Pesquisas Judiciarias do CNJ. O corpus processado contem `{len(corpus)}` documentos e {_evidence_axis_note(evidence)} consideradas para a etapa de sintese.

O estudo nao mede demanda de cursistas, orcamento, capacidade operacional das escolas ou prioridade politica. Ele organiza sinais documentais para apoiar decisao pedagogica posterior.

## 3. Metodo de priorizacao

A priorizacao usa um score composto:

`score_final = 0,45 * score_textual_norm + 0,30 * consistencia_evidencial + 0,25 * valor_institucional`

- `score_textual_norm`: intensidade lexical e contextual do trecho, limitada a 1,0.
- `consistencia_evidencial`: recorrencia do eixo e distribuicao em documentos distintos.
- `valor_institucional`: peso configurado por eixo tematico em `config/criterios_analiticos.yml`.
- faixas de decisao: alta (`>= 0,75`), media (`>= 0,50`) e baixa (`< 0,50`).

Calibracao: {calibration['descricao']}

## 4. Expansao do universo documental

{expansion_section}

## 5. Resultados priorizados

{matrix_table}

## 6. Portfolio recomendado

{portfolio_table}

## 7. Evidencias rastreaveis

{dossier_table}

## 8. Limitacoes e riscos

{_alerts_markdown(evidence)}

As evidencias automatizadas devem ser lidas como subsidio tecnico. A decisao final sobre oferta educacional, sequenciamento, carga horaria e publico prioritario deve considerar validacao institucional, disponibilidade de instrutores, calendario e capacidade de execucao.

## 9. Conclusao

O pacote produzido oferece uma base objetiva, rastreavel e replicavel para transformar producoes do CNJ em uma agenda inicial de capacitacao. A principal contribuicao e reduzir a dependencia de revisao manual massiva, mantendo transparencia metodologica, evidencia citavel e limites explicitos para uso institucional.
"""


def _expansion_section(
    corpus: pd.DataFrame,
    source_matrix: pd.DataFrame,
    normative_matrix: pd.DataFrame,
    offer_gap: pd.DataFrame,
) -> str:
    if "corpus_origem" not in corpus.columns and source_matrix.empty and offer_gap.empty:
        return "A publicacao usa a linha de base exploratoria original. A expansao multibase ainda nao foi executada para este ciclo."
    origin_table = (
        corpus.groupby(["corpus_origem", "fonte_tipo"], dropna=False)
        .agg(documentos=("doc_id", "nunique"))
        .reset_index()
        .sort_values("documentos", ascending=False)
    ) if {"corpus_origem", "fonte_tipo", "doc_id"}.issubset(corpus.columns) else pd.DataFrame()
    return "\n\n".join(
        [
            "O corpus expandido separa documentos de diagnostico, atos normativos, guias/manuais, noticias e ofertas formativas. Essa separacao evita que comunicacao institucional ou oferta de curso tenha o mesmo peso probatorio de pesquisa ou diagnostico.",
            "### Distribuicao por origem e tipo de fonte",
            _markdown_table(origin_table, [("corpus_origem", "Origem"), ("fonte_tipo", "Tipo de fonte"), ("documentos", "Documentos")], limit=12),
            "### Lacunas por tipo de fonte",
            _markdown_table(source_matrix, [("fonte_tipo", "Tipo de fonte"), ("achado_classe", "Classe"), ("eixo", "Eixo"), ("evidencias", "Evidencias"), ("documentos", "Documentos")], limit=12),
            "### Competencias requeridas por normas, guias e programas",
            _markdown_table(normative_matrix, [("eixo", "Eixo"), ("hipotese_competencia", "Competencia"), ("fonte_tipo", "Fonte"), ("evidencias", "Evidencias"), ("documentos", "Documentos")], limit=10),
            "### Mapa oferta versus lacuna",
            _markdown_table(offer_gap, [("eixo", "Eixo"), ("gaps_observados", "Gaps"), ("competencias_requeridas", "Competencias"), ("ofertas_formativas", "Ofertas"), ("status_mapeamento", "Leitura")], limit=10),
        ]
    )


def _portfolio_markdown(
    context: RunContext,
    portfolio: pd.DataFrame,
    matrix: pd.DataFrame,
    status_label: str,
) -> str:
    portfolio_table = _markdown_table(
        portfolio,
        [
            ("ordem", "Ordem"),
            ("faixa_prioridade", "Faixa"),
            ("categoria", "Tipo"),
            ("proposta", "Proposta"),
            ("publico_prioritario", "Publico"),
            ("competencias_centrais", "Competencias"),
            ("produto_esperado", "Produto esperado"),
            ("indicador_avaliacao", "Indicador"),
        ],
    )
    return f"""# Portfolio de Capacitacoes e Trilhas Baseado em Evidencias do CNJ

## Objetivo

Consolidar as lacunas priorizadas da linha de base `{context.run_id}` em uma proposta inicial de capacitacoes e trilhas para a ENAJU e escolas judiciais.

## Status

**{status_label}**

## Portfolio

{portfolio_table}

## Criterios de priorizacao

- score textual do trecho;
- consistencia evidencial por recorrencia e documentos distintos;
- valor institucional configurado por eixo;
- rebaixamento de itens sem classificacao tematica;
- leitura final condicionada a validacao pedagogica e institucional.

## Magnitude documental

{_markdown_table(matrix, [("proposta", "Proposta"), ("evidencias_total", "Evidencias"), ("documentos_impactados", "Documentos"), ("score_final", "Score final")], limit=10)}
"""
