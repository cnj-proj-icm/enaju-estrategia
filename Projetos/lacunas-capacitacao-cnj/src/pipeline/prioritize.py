from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

from .common import RunContext, json_loads, read_csv, write_csv, write_parquet

LOGGER = logging.getLogger(__name__)

VALID_CALIBRATION_DECISIONS = {"", "pendente", "gap_confirmado", "falso_positivo", "termo_ausente"}
DEFAULT_OUTPUT_COLUMNS = [
    "eixo",
    "proposta",
    "categoria",
    "evidencias_total",
    "documentos_impactados",
    "score_textual_medio",
    "consistencia_evidencial",
    "valor_institucional",
    "taxa_falso_positivo_estimada",
    "score_final",
    "faixa_prioridade",
    "magnitude_documental",
]


def _as_list(value: Any) -> list[str]:
    parsed = json_loads(value, [])
    if isinstance(parsed, str):
        return [item.strip() for item in parsed.split(";") if item.strip()]
    if isinstance(parsed, list):
        return [str(item).strip() for item in parsed if str(item).strip()]
    return []


def _explode_axes(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame.assign(eixo=pd.Series(dtype="object"))
    rows: list[dict[str, Any]] = []
    source = "eixos_revisados" if "eixos_revisados" in frame.columns else "eixos"
    for row in frame.to_dict("records"):
        value = row.get(source)
        if source == "eixos_revisados" and not str(value or "").strip():
            value = row.get("eixos")
        axes = _as_list(value) or ["nao_classificado"]
        for axis in axes:
            rows.append({**row, "eixo": axis})
    return pd.DataFrame(rows)


def _score_band(value: Any) -> str:
    score = pd.to_numeric(pd.Series([value]), errors="coerce").fillna(0).iloc[0]
    if score >= 10:
        return "alto"
    if score >= 3:
        return "medio"
    return "baixo"


def _priority_band(score: float, thresholds: dict[str, Any]) -> str:
    high = float(thresholds.get("alta", 0.75))
    medium = float(thresholds.get("media", 0.50))
    if score >= high:
        return "alta"
    if score >= medium:
        return "media"
    return "baixa"


def _proposal_for_axis(criteria: dict[str, Any], axis: str) -> dict[str, Any]:
    proposals = criteria.get("priorizacao_automatica", {}).get("propostas_formativas", {})
    proposal = dict(proposals.get(axis, {}))
    proposal.setdefault("categoria", "Hipotese")
    proposal.setdefault("proposta", axis.replace("_", " ").title())
    proposal.setdefault("publico_prioritario", "gestores e equipes tecnicas")
    proposal.setdefault("competencias_centrais", "analise de contexto, priorizacao e aplicacao institucional")
    proposal.setdefault("carga_horaria_sugerida", "12h a 16h")
    proposal.setdefault("modalidade_sugerida", "curso curto com oficina aplicada")
    proposal.setdefault("produto_esperado", "plano de aplicacao institucional")
    proposal.setdefault("indicador_avaliacao", "produto final avaliado por rubrica")
    return proposal


def _empty_outputs(context: RunContext) -> dict[str, Any]:
    write_csv(pd.DataFrame(columns=DEFAULT_OUTPUT_COLUMNS), context.paths.outputs / "matriz_lacunas_priorizadas.csv")
    write_csv(pd.DataFrame(), context.paths.outputs / "dossie_evidencias.csv")
    write_csv(pd.DataFrame(), context.paths.outputs / "trilhas_capacitacoes_evidencias.csv")
    write_csv(pd.DataFrame(), context.paths.processed / "evidencias_priorizadas.csv")
    write_parquet(pd.DataFrame(), context.paths.processed / "evidencias_priorizadas.parquet")
    return {"evidencias_priorizadas": 0, "lacunas_priorizadas": 0}


def _calibration_frame(context: RunContext) -> pd.DataFrame:
    path = context.paths.processed / "calibracao_analitica.csv"
    if not path.exists():
        return pd.DataFrame()
    return read_csv(path)


def _false_positive_by_axis(calibration: pd.DataFrame) -> dict[str, float | str]:
    if calibration.empty or "eixo" not in calibration.columns:
        return {}
    grouped = calibration.groupby("eixo", dropna=False).agg(
        revisados=("revisados", "sum"),
        falsos_positivos=("falsos_positivos", "sum"),
    )
    rates: dict[str, float | str] = {}
    for axis, row in grouped.iterrows():
        reviewed = int(row["revisados"])
        if reviewed:
            rates[str(axis)] = round(float(row["falsos_positivos"]) / reviewed, 4)
        else:
            rates[str(axis)] = ""
    return rates


def _build_calibration_analysis(frame: pd.DataFrame) -> pd.DataFrame:
    expanded = _explode_axes(frame)
    if expanded.empty:
        return pd.DataFrame(
            columns=[
                "tipo_amostra",
                "tipo_gap",
                "eixo",
                "score_faixa",
                "total_itens",
                "revisados",
                "gaps_confirmados",
                "falsos_positivos",
                "termos_ausentes",
                "pendentes",
                "taxa_falso_positivo",
            ]
        )
    expanded["tipo_gap"] = expanded.get("tipo_gap", "sem_match")
    expanded["tipo_gap"] = expanded["tipo_gap"].replace("", "sem_match").fillna("sem_match")
    expanded["eixo"] = expanded["eixo"].replace("", "nao_classificado").fillna("nao_classificado")
    expanded["score_faixa"] = expanded.get("score", 0).apply(_score_band)
    expanded["decisao_calibracao"] = expanded.get("decisao_calibracao", "").fillna("").astype(str).str.strip()
    expanded["revisado"] = ~expanded["decisao_calibracao"].isin(["", "pendente"])
    grouped = (
        expanded.groupby(["tipo_amostra", "tipo_gap", "eixo", "score_faixa"], dropna=False)
        .agg(
            total_itens=("decisao_calibracao", "count"),
            revisados=("revisado", "sum"),
            gaps_confirmados=("decisao_calibracao", lambda values: int((values == "gap_confirmado").sum())),
            falsos_positivos=("decisao_calibracao", lambda values: int((values == "falso_positivo").sum())),
            termos_ausentes=("decisao_calibracao", lambda values: int((values == "termo_ausente").sum())),
            pendentes=("decisao_calibracao", lambda values: int(values.isin(["", "pendente"]).sum())),
        )
        .reset_index()
    )
    grouped["taxa_falso_positivo"] = grouped.apply(
        lambda row: round(row["falsos_positivos"] / row["revisados"], 4) if row["revisados"] else "",
        axis=1,
    )
    return grouped.sort_values(["eixo", "tipo_gap", "score_faixa", "tipo_amostra"])


def import_calibration(context: RunContext, review_file: str | Path) -> pd.DataFrame:
    path = Path(review_file)
    if not path.is_absolute():
        path = context.paths.root / path
    sample = read_csv(path)
    if "decisao_calibracao" not in sample.columns:
        raise ValueError("Amostra de calibracao sem coluna obrigatoria: decisao_calibracao")
    decisions = sample["decisao_calibracao"].fillna("").astype(str).str.strip()
    invalid = sorted(set(decisions) - VALID_CALIBRATION_DECISIONS)
    if invalid:
        raise ValueError(f"Decisoes de calibracao invalidas: {invalid}")
    sample["decisao_calibracao"] = decisions
    analysis = _build_calibration_analysis(sample)
    write_csv(analysis, context.paths.processed / "calibracao_analitica.csv")
    context.update_manifest(
        "import-calibration",
        linhas_recebidas=len(sample),
        grupos_analiticos=len(analysis),
        revisados=int((~decisions.isin(["", "pendente"])).sum()),
        pendentes=int(decisions.isin(["", "pendente"]).sum()),
    )
    return analysis


def _evidence_source(context: RunContext) -> tuple[Path, str]:
    expanded = context.paths.processed / "trechos_candidatos_expandido.csv"
    if expanded.exists():
        return expanded, "trechos_candidatos_expandido"
    confirmed = context.paths.processed / "evidencias_confirmadas.csv"
    if confirmed.exists():
        return confirmed, "evidencias_confirmadas"
    return context.paths.processed / "trechos_candidatos.csv", "trechos_candidatos"


def prioritize_evidence(context: RunContext) -> dict[str, Any]:
    source_path, source_label = _evidence_source(context)
    evidence = read_csv(source_path)
    if evidence.empty:
        summary = _empty_outputs(context)
        context.update_manifest("prioritize", fonte=source_label, **summary)
        return summary

    criteria = context.criteria_config
    settings = criteria.get("priorizacao_automatica", {})
    weights = settings.get("pesos", {})
    thresholds = settings.get("limiares", {})
    values = settings.get("valor_institucional_por_eixo", {})

    expanded = _explode_axes(evidence)
    expanded["score"] = pd.to_numeric(expanded.get("score", 0), errors="coerce").fillna(0)
    if "peso_fonte" not in expanded.columns:
        expanded["peso_fonte"] = 1.0
    if "fonte_tipo" not in expanded.columns:
        expanded["fonte_tipo"] = "relatorio_diagnostico_pesquisa"
    if "achado_classe" not in expanded.columns:
        expanded["achado_classe"] = "gap_observado"
    expanded["peso_fonte"] = pd.to_numeric(expanded["peso_fonte"], errors="coerce").fillna(1.0)
    expanded["score_textual_norm"] = (expanded["score"] / 10).clip(upper=1.0) * expanded["peso_fonte"]

    axis_stats = (
        expanded.groupby("eixo", dropna=False)
        .agg(evidencias_eixo=("evidencia_id", "count"), documentos_eixo=("doc_id", "nunique"))
        .reset_index()
    )
    max_evidence = max(int(axis_stats["evidencias_eixo"].max()), 1)
    max_docs = max(int(axis_stats["documentos_eixo"].max()), 1)
    axis_stats["recorrencia_por_eixo"] = axis_stats["evidencias_eixo"] / max_evidence
    axis_stats["documentos_por_eixo"] = axis_stats["documentos_eixo"] / max_docs
    axis_stats["consistencia_evidencial"] = (
        0.5 * axis_stats["recorrencia_por_eixo"] + 0.5 * axis_stats["documentos_por_eixo"]
    )
    expanded = expanded.merge(axis_stats, on="eixo", how="left")
    expanded["valor_institucional"] = expanded["eixo"].map(values).fillna(settings.get("valor_padrao", 0.5)).astype(float)
    expanded["score_final"] = (
        float(weights.get("score_textual", 0.45)) * expanded["score_textual_norm"]
        + float(weights.get("consistencia_evidencial", 0.30)) * expanded["consistencia_evidencial"]
        + float(weights.get("valor_institucional", 0.25)) * expanded["valor_institucional"]
    )
    medium_threshold = float(thresholds.get("media", 0.50))
    unclassified = expanded["eixo"].eq("nao_classificado")
    expanded.loc[unclassified, "score_final"] = expanded.loc[unclassified, "score_final"].clip(
        upper=medium_threshold - 0.01
    )
    expanded["faixa_prioridade"] = expanded["score_final"].apply(lambda score: _priority_band(float(score), thresholds))

    calibration = _calibration_frame(context)
    fp_rates = _false_positive_by_axis(calibration)
    expanded["taxa_falso_positivo_estimada"] = expanded["eixo"].map(fp_rates).fillna("")

    proposals = expanded["eixo"].apply(lambda axis: _proposal_for_axis(criteria, str(axis)))
    expanded["categoria"] = proposals.apply(lambda item: item["categoria"])
    expanded["proposta"] = proposals.apply(lambda item: item["proposta"])
    expanded["score_final"] = expanded["score_final"].round(4)
    expanded["score_textual_norm"] = expanded["score_textual_norm"].round(4)
    expanded["consistencia_evidencial"] = expanded["consistencia_evidencial"].round(4)

    write_csv(expanded, context.paths.processed / "evidencias_priorizadas.csv")
    write_parquet(expanded, context.paths.processed / "evidencias_priorizadas.parquet")

    matrix = _build_priority_matrix(expanded, criteria, thresholds)
    dossier = _build_evidence_dossier(expanded)
    portfolio = _build_training_portfolio(matrix, criteria)
    by_source_type = _build_source_type_matrix(expanded)
    normative = _build_normative_competency_matrix(expanded)
    offer_gap = _build_offer_gap_map(expanded)
    write_csv(matrix, context.paths.outputs / "matriz_lacunas_priorizadas.csv")
    write_csv(dossier, context.paths.outputs / "dossie_evidencias.csv")
    write_csv(portfolio, context.paths.outputs / "trilhas_capacitacoes_evidencias.csv")
    write_csv(by_source_type, context.paths.outputs / "matriz_lacunas_por_tipo_fonte.csv")
    write_csv(normative, context.paths.outputs / "matriz_normativos_competencias.csv")
    write_csv(offer_gap, context.paths.outputs / "mapa_oferta_vs_lacuna.csv")

    summary = {
        "fonte": source_label,
        "evidencias_priorizadas": len(expanded),
        "lacunas_priorizadas": len(matrix),
        "evidencias_dossie": len(dossier),
        "tipos_fonte": int(expanded["fonte_tipo"].nunique()),
    }
    context.update_manifest("prioritize", **summary)
    LOGGER.info("Priorizacao concluida: %s evidencias, %s lacunas", len(expanded), len(matrix))
    return summary


def _build_priority_matrix(expanded: pd.DataFrame, criteria: dict[str, Any], thresholds: dict[str, Any]) -> pd.DataFrame:
    usable = expanded[expanded["eixo"] != "nao_classificado"].copy()
    if usable.empty:
        return pd.DataFrame(columns=DEFAULT_OUTPUT_COLUMNS)
    matrix = (
        usable.groupby(["eixo", "proposta", "categoria"], dropna=False)
        .agg(
            evidencias_total=("evidencia_id", "count"),
            documentos_impactados=("doc_id", "nunique"),
            score_textual_medio=("score_textual_norm", "mean"),
            consistencia_evidencial=("consistencia_evidencial", "mean"),
            valor_institucional=("valor_institucional", "mean"),
            score_final=("score_final", "mean"),
            taxa_falso_positivo_estimada=("taxa_falso_positivo_estimada", "first"),
        )
        .reset_index()
    )
    matrix["score_textual_medio"] = matrix["score_textual_medio"].round(4)
    matrix["consistencia_evidencial"] = matrix["consistencia_evidencial"].round(4)
    matrix["valor_institucional"] = matrix["valor_institucional"].round(4)
    matrix["score_final"] = matrix["score_final"].round(4)
    matrix["faixa_prioridade"] = matrix["score_final"].apply(lambda score: _priority_band(float(score), thresholds))
    matrix["magnitude_documental"] = matrix["evidencias_total"]
    return matrix.sort_values(["score_final", "evidencias_total", "documentos_impactados"], ascending=False)[
        DEFAULT_OUTPUT_COLUMNS
    ]


def _build_evidence_dossier(expanded: pd.DataFrame) -> pd.DataFrame:
    usable = expanded[expanded["eixo"] != "nao_classificado"].copy()
    if usable.empty:
        return pd.DataFrame()
    usable["trecho_curto"] = usable["trecho"].astype(str).str.replace(r"\s+", " ", regex=True).str.slice(0, 600)
    usable = usable.sort_values(["score_final", "score", "documentos_eixo"], ascending=False)
    top = usable.groupby(["eixo", "proposta"], dropna=False).head(3).copy()
    columns = [
        "eixo",
        "proposta",
        "categoria",
        "faixa_prioridade",
        "score_final",
        "score",
        "tipo_gap",
        "evidencia_id",
        "doc_id",
        "titulo",
        "pagina",
        "url",
        "hipotese_competencia",
        "trecho_curto",
    ]
    return top[[column for column in columns if column in top.columns]]


def _build_training_portfolio(matrix: pd.DataFrame, criteria: dict[str, Any]) -> pd.DataFrame:
    if matrix.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for order, row in enumerate(matrix.to_dict("records"), start=1):
        proposal = _proposal_for_axis(criteria, row["eixo"])
        rows.append(
            {
                "ordem": order,
                "categoria": row["categoria"],
                "proposta": row["proposta"],
                "eixo": row["eixo"],
                "faixa_prioridade": row["faixa_prioridade"],
                "score_final": row["score_final"],
                "evidencias_total": row["evidencias_total"],
                "documentos_impactados": row["documentos_impactados"],
                "magnitude": row["magnitude_documental"],
                "publico_prioritario": proposal["publico_prioritario"],
                "competencias_centrais": proposal["competencias_centrais"],
                "carga_horaria_sugerida": proposal["carga_horaria_sugerida"],
                "modalidade_sugerida": proposal["modalidade_sugerida"],
                "produto_esperado": proposal["produto_esperado"],
                "indicador_avaliacao": proposal["indicador_avaliacao"],
            }
        )
    return pd.DataFrame(rows)


def _build_source_type_matrix(expanded: pd.DataFrame) -> pd.DataFrame:
    if expanded.empty:
        return pd.DataFrame()
    matrix = (
        expanded.groupby(["fonte_tipo", "achado_classe", "eixo"], dropna=False)
        .agg(
            evidencias=("evidencia_id", "count"),
            documentos=("doc_id", "nunique"),
            score_final_medio=("score_final", "mean"),
            peso_fonte_medio=("peso_fonte", "mean"),
        )
        .reset_index()
        .sort_values(["evidencias", "documentos"], ascending=False)
    )
    matrix["score_final_medio"] = matrix["score_final_medio"].round(4)
    matrix["peso_fonte_medio"] = matrix["peso_fonte_medio"].round(4)
    return matrix


def _build_normative_competency_matrix(expanded: pd.DataFrame) -> pd.DataFrame:
    if expanded.empty:
        return pd.DataFrame()
    normative = expanded[
        expanded["achado_classe"].eq("competencia_requerida")
        | expanded["fonte_tipo"].isin(["ato_normativo", "manual_guia_cartilha"])
    ].copy()
    if normative.empty:
        return pd.DataFrame()
    normative["hipotese_competencia"] = normative["hipotese_competencia"].replace("", "competencia_a_qualificar")
    matrix = (
        normative.groupby(["eixo", "hipotese_competencia", "fonte_tipo"], dropna=False)
        .agg(
            evidencias=("evidencia_id", "count"),
            documentos=("doc_id", "nunique"),
            score_final_medio=("score_final", "mean"),
        )
        .reset_index()
        .sort_values(["evidencias", "documentos"], ascending=False)
    )
    matrix["score_final_medio"] = matrix["score_final_medio"].round(4)
    return matrix


def _build_offer_gap_map(expanded: pd.DataFrame) -> pd.DataFrame:
    if expanded.empty:
        return pd.DataFrame()
    pivot = (
        expanded.groupby(["eixo", "achado_classe"], dropna=False)
        .agg(evidencias=("evidencia_id", "count"), documentos=("doc_id", "nunique"))
        .reset_index()
    )
    evidence = pivot.pivot_table(index="eixo", columns="achado_classe", values="evidencias", aggfunc="sum", fill_value=0)
    docs = pivot.pivot_table(index="eixo", columns="achado_classe", values="documentos", aggfunc="sum", fill_value=0)
    rows: list[dict[str, Any]] = []
    for axis in sorted(set(evidence.index) | set(docs.index)):
        gap = int(evidence.get("gap_observado", pd.Series()).get(axis, 0))
        required = int(evidence.get("competencia_requerida", pd.Series()).get(axis, 0))
        offer = int(evidence.get("oferta_formativa", pd.Series()).get(axis, 0))
        status = "lacuna_sem_oferta_mapeada" if gap and not offer else "oferta_e_lacuna_mapeadas" if gap and offer else "competencia_ou_oferta_sem_gap"
        rows.append(
            {
                "eixo": axis,
                "gaps_observados": gap,
                "competencias_requeridas": required,
                "ofertas_formativas": offer,
                "documentos_com_gap": int(docs.get("gap_observado", pd.Series()).get(axis, 0)),
                "documentos_com_oferta": int(docs.get("oferta_formativa", pd.Series()).get(axis, 0)),
                "status_mapeamento": status,
            }
        )
    return pd.DataFrame(rows).sort_values(["gaps_observados", "competencias_requeridas"], ascending=False)
