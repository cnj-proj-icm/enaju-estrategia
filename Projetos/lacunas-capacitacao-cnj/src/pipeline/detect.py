from __future__ import annotations

import logging
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

from .common import (
    RunContext,
    json_dumps,
    normalize_text,
    read_csv,
    stable_id,
    write_csv,
    write_parquet,
)

LOGGER = logging.getLogger(__name__)
CALIBRATION_SEED = 20260531


def _contains_term(normalized_text: str, term: str) -> bool:
    normalized_term = normalize_text(term)
    pattern = r"(?<!\w)" + re.escape(normalized_term).replace(r"\ ", r"\s+") + r"(?!\w)"
    return re.search(pattern, normalized_text) is not None


def _matched_terms(text: str, terms: list[str]) -> list[str]:
    normalized = normalize_text(text)
    return sorted({term for term in terms if _contains_term(normalized, term)})


def evaluate_segment(text: str, criteria: dict[str, Any]) -> dict[str, Any]:
    groups: dict[str, list[str]] = {}
    score = 0
    for group_name, group in criteria["grupos"].items():
        matches = _matched_terms(text, group["termos"])
        if group_name == "A_lacuna_direta" and "deficiencia" in matches:
            without_disability_phrase = normalize_text(text).replace("pessoas com deficiencia", " ")
            if not _contains_term(without_disability_phrase, "deficiencia"):
                matches.remove("deficiencia")
        if matches:
            groups[group_name] = matches
            score += int(group["peso"]) * len(matches)
    has_a = "A_lacuna_direta" in groups
    has_b = "B_necessidade_formativa" in groups
    has_c = "C_problema_organizacional" in groups
    if has_a and has_b:
        score += int(criteria["bonus"]["coocorrencia_A_B"]["peso"])
    action_terms = _matched_terms(text, criteria["bonus"]["verbos_acao"]["termos"])
    if action_terms:
        score += int(criteria["bonus"]["verbos_acao"]["peso"])
    axes = [
        axis
        for axis, values in criteria["eixos"].items()
        if _matched_terms(text, values["termos"])
    ]
    hypotheses = [
        item["hipotese"]
        for item in criteria["hipoteses_competencia"]
        if _matched_terms(text, item["gatilhos"])
    ]
    if has_a and any(name != "A_lacuna_direta" for name in groups):
        gap_type = "explicito"
    elif has_c:
        gap_type = "implicito"
    else:
        gap_type = "potencial"
    return {
        "grupos_encontrados": groups,
        "termos_encontrados": sorted({term for terms in groups.values() for term in terms}),
        "verbos_acao": action_terms,
        "eixos": axes or ["nao_classificado"],
        "hipotese_competencia": "; ".join(sorted(set(hypotheses))),
        "tipo_gap": gap_type,
        "score": score,
    }


def classify_finding(result: dict[str, Any], metadata: dict[str, Any]) -> str:
    groups = result.get("grupos_encontrados", {})
    source_type = str(metadata.get("fonte_tipo", "")).strip()
    use = str(metadata.get("uso_metodologico", "")).strip()
    if source_type == "oferta_formativa" or use == "oferta_formativa":
        if "A_lacuna_direta" not in groups and "C_problema_organizacional" not in groups:
            return "oferta_formativa"
    if source_type == "ato_normativo" or use == "competencia_requerida":
        if "A_lacuna_direta" not in groups:
            return "competencia_requerida"
    if "F_competencia_requerida" in groups and "A_lacuna_direta" not in groups:
        return "competencia_requerida"
    if "G_oferta_formativa" in groups and "A_lacuna_direta" not in groups:
        return "oferta_formativa"
    return "gap_observado"


def _merge_overlapping(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["doc_id"], int(row["pagina"]))].append(row)
    merged: list[dict[str, Any]] = []
    for _, candidates in grouped.items():
        candidates.sort(key=lambda item: (int(item["char_inicio"]), int(item["char_fim"])))
        clusters: list[list[dict[str, Any]]] = []
        for candidate in candidates:
            if not clusters or int(candidate["char_inicio"]) > max(int(row["char_fim"]) for row in clusters[-1]):
                clusters.append([candidate])
            else:
                clusters[-1].append(candidate)
        for cluster in clusters:
            best = max(cluster, key=lambda item: (int(item["score"]), -len(item["trecho"])))
            best = dict(best)
            best["segmentos_agregados"] = len(cluster)
            merged.append(best)
    return merged


def detect_candidates(context: RunContext) -> pd.DataFrame:
    expanded = (context.paths.processed / "segmentos_expandido.parquet").exists()
    segment_path = context.paths.processed / ("segmentos_expandido.parquet" if expanded else "segmentos.parquet")
    corpus_path = context.paths.processed / ("corpus_documentos_expandido.csv" if expanded else "corpus_documentos.csv")
    output_suffix = "_expandido" if expanded else ""
    segments = pd.read_parquet(segment_path)
    corpus = read_csv(corpus_path)
    criteria = context.criteria_config
    preferred = segments[segments["tipo_segmento"] == "janela"].copy()
    metadata_by_doc = {row["doc_id"]: row for row in corpus.to_dict("records")}
    rows: list[dict[str, Any]] = []
    no_match_rows: list[dict[str, Any]] = []
    for segment in preferred.to_dict("records"):
        result = evaluate_segment(segment["trecho"], criteria)
        if not result["termos_encontrados"]:
            no_match_rows.append(segment)
            continue
        metadata = metadata_by_doc.get(segment["doc_id"], {})
        rows.append(
            {
                **segment,
                **result,
                "achado_classe": classify_finding(result, metadata),
                "termos_encontrados": json_dumps(result["termos_encontrados"]),
                "grupos_encontrados": json_dumps(result["grupos_encontrados"]),
                "verbos_acao": json_dumps(result["verbos_acao"]),
                "eixos": json_dumps(result["eixos"]),
            }
        )
    candidates = _merge_overlapping(rows)
    metadata_columns = [
        "doc_id",
        "titulo",
        "ano",
        "url",
        "secao_portal",
        "prioridade_analitica",
        "snapshot_sha256",
        "fonte_tipo",
        "peso_fonte",
        "forca_probatoria",
        "uso_metodologico",
    ]
    for column, default in (
        ("fonte_tipo", "relatorio_diagnostico_pesquisa"),
        ("peso_fonte", 1.0),
        ("forca_probatoria", "alta"),
        ("uso_metodologico", "gap_observado"),
    ):
        if column not in corpus.columns:
            corpus[column] = default
    metadata = corpus[metadata_columns]
    frame = pd.DataFrame(candidates)
    if frame.empty:
        frame = pd.DataFrame(columns=["doc_id"])
    frame = frame.merge(metadata, on="doc_id", how="left")
    frame["run_id"] = context.run_id
    frame["as_of"] = context.as_of
    frame["versao_criterios"] = criteria["versao"]
    frame["evidencia_id"] = frame.apply(
        lambda row: stable_id("ev", row["doc_id"], row["pagina"], row["char_inicio"], row["char_fim"]),
        axis=1,
    )
    output_columns = [
        "run_id",
        "as_of",
        "snapshot_sha256",
        "versao_criterios",
        "evidencia_id",
        "doc_id",
        "titulo",
        "ano",
        "url",
        "secao_portal",
        "prioridade_analitica",
        "fonte_tipo",
        "peso_fonte",
        "forca_probatoria",
        "uso_metodologico",
        "pagina",
        "tipo_segmento",
        "char_inicio",
        "char_fim",
        "trecho",
        "termos_encontrados",
        "grupos_encontrados",
        "verbos_acao",
        "eixos",
        "tipo_gap",
        "achado_classe",
        "hipotese_competencia",
        "score",
        "segmentos_agregados",
    ]
    frame = frame[output_columns].sort_values(["score", "doc_id", "pagina"], ascending=[False, True, True])
    write_csv(frame, context.paths.processed / f"trechos_candidatos{output_suffix}.csv")
    write_parquet(frame, context.paths.processed / f"trechos_candidatos{output_suffix}.parquet")
    if expanded:
        write_csv(frame, context.paths.processed / "trechos_candidatos.csv")
        write_parquet(frame, context.paths.processed / "trechos_candidatos.parquet")
    _write_review_queue(context, frame)
    _write_calibration_sample(context, frame, no_match_rows)
    context.update_manifest(
        "detect-expanded" if expanded else "detect",
        candidatos=len(frame),
        fila_revisao=len(read_csv(context.paths.processed / "fila_revisao.csv")),
        segmentos_sem_match=len(no_match_rows),
        corpus="expandido" if expanded else "baseline",
    )
    LOGGER.info("Deteccao concluida: %s candidatos", len(frame))
    return frame


def _write_review_queue(context: RunContext, frame: pd.DataFrame) -> None:
    if frame.empty:
        queue = frame.copy()
    else:
        queue = frame[
            frame["tipo_gap"].isin(["explicito", "implicito"])
            | ((frame["tipo_gap"] == "potencial") & (frame["score"] >= 3))
        ].copy()
    for column, default in (
        ("decisao_revisor", "pendente"),
        ("tipo_gap_revisado", ""),
        ("eixos_revisados", ""),
        ("hipotese_competencia_revisada", ""),
        ("uso_relatorio", "false"),
        ("nota_revisor", ""),
        ("revisor_id", ""),
        ("data_revisao", ""),
        ("auditoria_status", "pendente"),
        ("auditor_id", ""),
        ("nota_auditoria", ""),
        ("conciliacao_status", "pendente"),
        ("nota_conciliacao", ""),
    ):
        queue[column] = default
    write_csv(queue, context.paths.processed / "fila_revisao.csv")


def _write_calibration_sample(
    context: RunContext, frame: pd.DataFrame, no_match_rows: list[dict[str, Any]]
) -> None:
    rng = random.Random(CALIBRATION_SEED)
    ordered = frame.sort_values("score", ascending=False)
    top = ordered.head(50).copy()
    remaining = ordered.iloc[len(top):]
    random_candidates = remaining.sample(
        n=min(50, len(remaining)), random_state=CALIBRATION_SEED
    ) if len(remaining) else remaining
    no_match = rng.sample(no_match_rows, k=min(30, len(no_match_rows)))
    rows: list[dict[str, Any]] = []
    for kind, sample in (("top_score", top), ("candidato_aleatorio", random_candidates)):
        for row in sample.to_dict("records"):
            rows.append({"tipo_amostra": kind, **row, "decisao_calibracao": "", "nota_calibracao": ""})
    for row in no_match:
        rows.append(
            {
                "tipo_amostra": "sem_match",
                **row,
                "decisao_calibracao": "",
                "nota_calibracao": "",
            }
        )
    write_csv(rows, context.paths.processed / "amostra_calibracao.csv")


def import_review(context: RunContext, review_file: str) -> pd.DataFrame:
    path = Path(review_file)
    if not path.is_absolute():
        path = context.paths.root / path
    queue = read_csv(path)
    required = {
        "evidencia_id",
        "decisao_revisor",
        "auditoria_status",
        "conciliacao_status",
    }
    missing = required - set(queue.columns)
    if missing:
        raise ValueError(f"Fila revisada sem colunas obrigatorias: {sorted(missing)}")
    valid_decisions = {"confirmado", "ajustado", "descartado", "pendente"}
    invalid = sorted(set(queue["decisao_revisor"]) - valid_decisions)
    if invalid:
        raise ValueError(f"Decisoes invalidas: {invalid}")
    confirmed = queue[queue["decisao_revisor"].isin(["confirmado", "ajustado"])].copy()
    confirmed = confirmed[
        confirmed["auditoria_status"].isin(["aprovado", "nao_selecionado"])
        & confirmed["conciliacao_status"].isin(["conciliado", "nao_necessaria"])
    ].copy()
    write_csv(confirmed, context.paths.processed / "evidencias_confirmadas.csv")
    write_parquet(confirmed, context.paths.processed / "evidencias_confirmadas.parquet")
    context.update_manifest(
        "import-review",
        linhas_recebidas=len(queue),
        evidencias_confirmadas=len(confirmed),
        pendencias=int((queue["decisao_revisor"] == "pendente").sum()),
    )
    return confirmed
