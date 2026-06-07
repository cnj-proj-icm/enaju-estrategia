from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

from .common import RunContext, json_loads, read_csv, write_csv
from .expanded import DISCOVERY_TERMS, SOURCE_POLICIES
from .sources import enabled_sources

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
        return ["Nenhuma evidência automática foi detectada para este recorte."]

    base = evidence.drop_duplicates("evidencia_id").copy() if "evidencia_id" in evidence.columns else evidence
    scores = _numeric_series(base, "score")
    low_confidence = int((scores < 3).sum())
    if low_confidence:
        alerts.append(
            f"{low_confidence} trechos apresentam score textual bruto baixo (< 3); devem ser lidos como hipóteses técnicas."
        )

    if {"doc_id", "trecho"}.issubset(base.columns):
        duplicate_pairs = int(base.duplicated(subset=["doc_id", "trecho"]).sum())
        if duplicate_pairs:
            alerts.append(
                f"{duplicate_pairs} evidências repetem o mesmo documento e trecho; a síntese consolida a mensagem para reduzir duplicidade."
            )

    if "tipo_gap" in base.columns:
        potential = int((base["tipo_gap"] == "potencial").sum())
        if potential:
            alerts.append(
                f"{potential} evidências foram classificadas como potenciais; elas apoiam recomendações, mas não constituem conclusões institucionais isoladas."
            )

    if "taxa_falso_positivo_estimada" in evidence.columns:
        known_rates = pd.to_numeric(evidence["taxa_falso_positivo_estimada"], errors="coerce").dropna()
        if not known_rates.empty:
            alerts.append(
                f"A maior taxa de falso positivo estimada na calibração amostral foi {known_rates.max():.1%}."
            )
    if "score_final" in evidence.columns and low_confidence:
        alerts.append(
            "O score textual bruto usa escala própria de detecção lexical; o score final é normalizado entre 0 e 1 após ponderação por consistência evidencial e valor institucional."
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
            "descricao": "A amostra de calibração foi gerada, mas ainda não há CSV preenchido importado.",
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
        description = f"Calibração amostral importada, com {reviewed} decisões revisadas nos grupos analíticos."
        status = "calibracao_amostral_importada"
    else:
        description = "Arquivo de calibração analítica existe, mas não contém decisões revisadas."
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
        return "PROPOSTA TÉCNICA - priorização automatizada com calibração amostral"
    if prioritized:
        return "PROPOSTA TÉCNICA - priorização automatizada com amostra de calibração estruturada"
    return "PROPOSTA TÉCNICA - candidatos automatizados ainda sem matriz de priorização"


def _evidence_count(evidence: pd.DataFrame) -> int:
    if "evidencia_id" in evidence.columns:
        return int(evidence["evidencia_id"].nunique())
    return len(evidence)


def _evidence_axis_note(evidence: pd.DataFrame) -> str:
    unique = _evidence_count(evidence)
    if len(evidence) == unique:
        return f"{unique}"
    return f"{unique} evidências únicas em {len(evidence)} linhas evidência-eixo"


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
        return "_Não há registros disponíveis._"
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


def _offer_gap_display(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    display = frame.copy()
    if "leitura_interpretativa" not in display.columns and "status_mapeamento" in display.columns:
        labels = {
            "lacuna_forte_com_baixa_oferta": "lacuna forte com baixa oferta mapeada",
            "lacuna_sem_oferta_mapeada": "lacuna sem oferta mapeada",
            "lacuna_forte_com_oferta_parcial": "lacuna forte com oferta parcial",
            "lacuna_forte_com_oferta_existente": "lacuna forte com oferta existente",
            "lacuna_moderada_com_oferta_existente": "lacuna moderada com oferta existente",
            "competencia_normativa_com_oferta_mapeada": "competência normativa com oferta mapeada",
            "competencia_normativa_sem_diagnostico": "competência normativa sem diagnóstico",
            "oferta_sem_gap_demonstrado": "oferta existente sem gap demonstrado",
            "revisao_tematica_pendente": "revisão temática pendente",
            "sem_sinal_suficiente": "sem sinal suficiente",
        }
        display["leitura_interpretativa"] = display["status_mapeamento"].map(labels).fillna(
            display["status_mapeamento"].astype(str).str.replace("_", " ")
        )
    return display


def _axis_lines(by_axis: pd.DataFrame, limit: int = 10) -> str:
    return "\n".join(
        f"- `{row['eixo']}`: {row['evidencias']} evidências em {row['documentos']} documentos ({row['secao_portal']})"
        for row in by_axis.head(limit).to_dict("records")
    ) or "- Nenhuma evidência disponível."


def _matrix_lines(matrix: pd.DataFrame, limit: int = 8) -> str:
    if matrix.empty:
        return "- Matriz de lacunas priorizadas ainda não gerada."
    return "\n".join(
        f"- {row['proposta']}: score final `{row['score_final']}`, faixa `{row['faixa_prioridade']}`, "
        f"{row['evidencias_total']} evidências em {row['documentos_impactados']} documentos."
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
    return f"""# Relatório de Validação

## Status

**{status_label}**

## Linha de base

- `run_id`: `{context.run_id}`
- data de corte editorial: `{context.as_of}`
- fonte analítica usada nos outputs: `{source_label}`
- documentos no corpus processado: `{len(corpus)}`
- evidências consideradas: `{_evidence_axis_note(evidence)}`

## Calibração amostral

{calibration['descricao']}

- decisões revisadas: `{calibration['revisados']}`
- pendências registradas: `{calibration['pendentes']}`
- taxa de falso positivo estimada: `{calibration['taxa_falso_positivo']}`

## Alertas de risco

{_alerts_markdown(evidence)}

## Critérios de aceite

- snapshot e hash registrados em `data/processed/manifest_run.json`;
- PDFs, textos e segmentos rastreáveis por `doc_id`;
- classificação automática identificada pela versão dos critérios;
- score composto documentado em `config/criterios_analiticos.yml`;
- resultados apresentados como proposta técnica, não como deliberação institucional final.
"""


def _executive_markdown(
    context: RunContext,
    corpus: pd.DataFrame,
    evidence: pd.DataFrame,
    by_axis: pd.DataFrame,
    matrix: pd.DataFrame,
    status_label: str,
) -> str:
    return f"""# Síntese Executiva - Lacunas de Capacitação em Produções do CNJ

## Status

**{status_label}**

## Recorte

A linha de base `{context.run_id}` usa a fotografia editorial do portal de Pesquisas Judiciárias do CNJ em `{context.as_of}`. O corpus processado contém `{len(corpus)}` documentos e {_evidence_axis_note(evidence)} consideradas.

## Lacunas e trilhas priorizadas

{_matrix_lines(matrix, limit=8)}

## Eixos em destaque

{_axis_lines(by_axis, limit=12)}

## Uso recomendado

Este documento é uma proposta técnica baseada em evidências automatizadas, matriz de priorização e calibração amostral quando importada. Ele apoia decisão pedagógica e planejamento, mas não substitui validação institucional final.

## Limites

- o corpus representa o portal e a data de corte, não todo o Poder Judiciário;
- menções a capacitação não são tratadas automaticamente como lacunas;
- hipóteses de competência exigem validação institucional antes de orientar oferta educacional definitiva.
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
    return f"""# Relatório Automatizado Publicável - ENAJU/CNJ

## Status executivo

**{status_label}**

Este produto organiza uma proposta técnica de priorização de lacunas de capacitação com base em evidências documentais rastreáveis, score composto e alertas de risco. A leitura correta é de apoio à decisão, sem substituir a deliberação institucional da ENAJU ou das escolas judiciais.

## Resumo operacional

- run_id: `{context.run_id}`
- data de corte editorial: `{context.as_of}`
- documentos no corpus: `{len(corpus)}`
- evidências consideradas: `{_evidence_axis_note(evidence)}`
- score textual médio: `{round(float(scores.mean()), 2) if not evidence.empty else 0.0}`
- score final médio: `{round(float(final_scores.mean()), 4) if "score_final" in evidence.columns else "não gerado"}`
- calibração: `{calibration['status']}`

## Lacunas priorizadas

{_matrix_lines(matrix, limit=10)}

## Eixos documentais

{_axis_lines(by_axis, limit=10)}

## Alertas de risco

{_alerts_markdown(evidence)}

## Recomendação de uso

- Usar como proposta técnica para planejamento de capacitações e trilhas.
- Cruzar os achados com prioridades pedagógicas, capacidade operacional e agenda institucional.
- Registrar qualquer decisão final em ata, parecer ou documento institucional próprio.
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
            ("evidencias_total", "Evidências"),
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
            ("publico_prioritario", "Público prioritário"),
            ("carga_horaria_sugerida", "Carga horária"),
            ("modalidade_sugerida", "Modalidade"),
        ],
        limit=10,
    )
    dossier_table = _markdown_table(
        dossier,
        [
            ("proposta", "Proposta"),
            ("titulo", "Documento"),
            ("pagina", "Página"),
            ("score_final", "Score final"),
            ("aderencia_eixo", "Aderência"),
            ("observacao_curadoria", "Nota de curadoria"),
            ("trecho_curto", "Evidência rastreável"),
        ],
        limit=18,
    )
    expansion_section = _expansion_section(corpus, source_matrix, normative_matrix, offer_gap)
    methodology_section = _methodology_section(context, corpus, evidence, source_matrix, calibration)
    robust_plan_section = _robust_gap_plan_section(matrix, offer_gap, source_matrix, normative_matrix)
    return f"""# Modelo de priorização de capacitações para escolas judiciais a partir de evidências documentais do CNJ

## 1. Resumo executivo

Este documento apresenta uma proposta técnica para identificar lacunas de capacitação em produções do CNJ, distinguir gaps observados de competências requeridas por normas e ofertas formativas existentes, e converter esse diagnóstico em um plano de aprofundamento analítico. O produto combina coleta documental, expansão multibase, identificação automatizada de evidências, score composto, matriz de priorização, alertas de risco e plano de validação.

**Status da entrega:** {status_label}.

## 2. Corpus e alcance

A linha de base `{context.run_id}` considera a fotografia editorial de `{context.as_of}` do portal de Pesquisas Judiciárias do CNJ. O corpus processado contém `{len(corpus)}` documentos e {_evidence_axis_note(evidence)} consideradas para a etapa de síntese.

O estudo não mede demanda de cursistas, orçamento, capacidade operacional das escolas ou prioridade política. Ele organiza sinais documentais para apoiar decisão pedagógica posterior.

## 3. Método utilizado e justificativa da escolha

{methodology_section}

## 4. Expansão do universo documental

{expansion_section}

## 5. Resultados priorizados

{matrix_table}

## 6. Portfólio preliminar para validação

{portfolio_table}

## 7. Evidências rastreáveis

{dossier_table}

## 8. Limitações e riscos

{_alerts_markdown(evidence)}

As evidências automatizadas devem ser lidas como subsídio técnico. A decisão final sobre oferta educacional, sequenciamento, carga horária e público prioritário deve considerar validação institucional, disponibilidade de instrutores, calendário e capacidade de execução.

## 9. Plano proposto para análise robusta dos gaps

{robust_plan_section}

## 10. Conclusão

O pacote produzido oferece uma base objetiva, rastreável e replicável para transformar produções do CNJ em uma agenda inicial de capacitação. A principal contribuição é criar um funil metodológico: primeiro identifica sinais documentais em escala, depois distingue a natureza da evidência, em seguida prioriza e, por fim, direciona uma análise humana mais robusta apenas para os gaps de maior relevância, risco ou potencial de decisão.
"""


def _inline_terms(values: list[Any] | tuple[Any, ...]) -> str:
    return ", ".join(f"`{value}`" for value in values)


def _search_strings_section(context: RunContext) -> str:
    criteria = context.criteria_config
    expansion_config = context.pipeline_config.get("expansao_corpus", {})
    try:
        source_rows = enabled_sources(context.paths.config / "sources.yml")
    except FileNotFoundError:
        source_rows = []
    source_table = pd.DataFrame(
        [
            {
                "fonte": source["name"],
                "tipo": source["type"],
                "prioridade": source["priority"],
                "url": source["url"],
            }
            for source in source_rows
        ]
    )
    group_rows = [
        {
            "grupo": group_name,
            "peso": group.get("peso", ""),
            "strings": _inline_terms(group.get("termos", [])),
        }
        for group_name, group in criteria.get("grupos", {}).items()
    ]
    axis_rows = [
        {
            "eixo": axis_name,
            "strings": _inline_terms(values.get("termos", [])),
        }
        for axis_name, values in criteria.get("eixos", {}).items()
    ]
    hypothesis_rows = [
        {
            "hipotese": item.get("hipotese", ""),
            "gatilhos": _inline_terms(item.get("gatilhos", [])),
        }
        for item in criteria.get("hipoteses_competencia", [])
    ]
    source_policy_rows = [
        {
            "fonte_tipo": source_type,
            "forca_probatoria": policy[0],
            "peso_fonte": policy[1],
            "uso_metodologico": policy[2],
        }
        for source_type, policy in SOURCE_POLICIES.items()
    ]
    bonus = criteria.get("bonus", {})
    action_terms = bonus.get("verbos_acao", {}).get("termos", [])
    allowed_domains = expansion_config.get("allowed_domains", [])
    return f"""### 3.5. Strings de busca para formação do corpus

A formação do corpus expandido partiu de páginas-semente configuradas, e não de uma busca livre na internet. O crawler visitou as fontes abaixo e, a partir delas, seguiu links internos quando a URL, o texto da âncora, o título ou o início do conteúdo continham termos de descoberta relacionados a capacitação, competência, publicações, normativos, programas ou notícias.

{_markdown_table(source_table, [("fonte", "Fonte"), ("tipo", "Tipo"), ("prioridade", "Prioridade"), ("url", "URL")])}

Os domínios autorizados para descoberta foram: {_inline_terms(allowed_domains)}. A janela metodológica configurada foi de `{expansion_config.get('ano_inicial', 2021)}` até a data de execução; normas estruturantes antigas puderam ser preservadas quando descobertas por fonte institucional vigente.

As strings de descoberta usadas para formar o corpus foram:

{_inline_terms(tuple(DISCOVERY_TERMS))}

Essas strings foram aplicadas de forma normalizada: o texto foi convertido para caixa baixa, com acentos removidos para comparação e espaços colapsados. Na descoberta de corpus, a presença de uma string funcionou como filtro de relevância para seguir links ou manter metadados; ela não significou, sozinha, que havia uma lacuna confirmada.

### 3.6. Strings usadas na análise dos gaps

Depois de formado o corpus, a análise textual usou outro conjunto de strings, mais específico, registrado em `config/criterios_analiticos.yml`. Diferentemente da descoberta de corpus, aqui as strings acionam grupos com pesos, classes de achado, eixos temáticos e hipóteses de competência.

As regras trabalham com correspondência literal normalizada, com fronteiras de palavra e espaços flexíveis em expressões compostas. Isso significa que `falta de` e `necessidade de`, por exemplo, são buscadas como expressões textuais rastreáveis, não como inferência semântica livre. A decisão foi manter regras auditáveis e reprodutíveis antes de introduzir classificação assistida por modelo.

#### Grupos analíticos e pesos

{_markdown_table(pd.DataFrame(group_rows), [("grupo", "Grupo"), ("peso", "Peso"), ("strings", "Strings")])}

#### Bônus de coocorrência e verbos de ação

- Coocorrência entre lacuna direta e necessidade formativa: peso `{bonus.get('coocorrencia_A_B', {}).get('peso', '')}`.
- Verbos de ação que reforçam orientação para desenvolvimento: {_inline_terms(action_terms)}.

#### Strings de classificação por eixo

{_markdown_table(pd.DataFrame(axis_rows), [("eixo", "Eixo"), ("strings", "Strings")])}

#### Gatilhos para hipóteses de competência

{_markdown_table(pd.DataFrame(hypothesis_rows), [("hipotese", "Hipótese de competência"), ("gatilhos", "Gatilhos textuais")])}

#### Peso metodológico por tipo de fonte

Nem toda string tem a mesma força conforme a fonte. Por isso, depois da detecção textual, o achado é ponderado por tipo de documento:

{_markdown_table(pd.DataFrame(source_policy_rows), [("fonte_tipo", "Tipo de fonte"), ("forca_probatoria", "Força probatória"), ("peso_fonte", "Peso"), ("uso_metodologico", "Uso metodológico")])}

Em termos práticos: relatórios e diagnósticos pesam mais para `gap_observado`; atos normativos pesam mais para `competencia_requerida`; cursos e notícias entram como contexto ou oferta formativa, com menor peso para não dominar a priorização.
"""


def _methodology_section(
    context: RunContext,
    corpus: pd.DataFrame,
    evidence: pd.DataFrame,
    source_matrix: pd.DataFrame,
    calibration: dict[str, Any],
) -> str:
    source_counts = (
        corpus.groupby("fonte_tipo", dropna=False)
        .agg(documentos=("doc_id", "nunique"))
        .reset_index()
        .sort_values("documentos", ascending=False)
    ) if {"fonte_tipo", "doc_id"}.issubset(corpus.columns) else pd.DataFrame()
    class_counts = (
        evidence.groupby("achado_classe", dropna=False)
        .agg(evidencias=("evidencia_id", "nunique"), documentos=("doc_id", "nunique"))
        .reset_index()
        .sort_values("evidencias", ascending=False)
    ) if {"achado_classe", "evidencia_id", "doc_id"}.issubset(evidence.columns) else pd.DataFrame()
    return f"""### 3.1. Problema metodológico enfrentado

A pergunta de pesquisa não é simplesmente "quais palavras aparecem nos documentos do CNJ?". O desafio é identificar, em um conjunto heterogêneo de fontes, sinais que possam indicar necessidade de desenvolvimento de competências no Poder Judiciário. Isso exige separar três coisas que costumam aparecer misturadas no texto institucional:

- `gap_observado`: relatórios, diagnósticos ou pesquisas apontam dificuldade, ausência, carência, baixa adesão, insuficiência, falta de padronização ou necessidade de capacitação.
- `competencia_requerida`: resoluções, portarias, programas, guias ou manuais estabelecem uma capacidade esperada, uma obrigação de implementação ou uma competência institucional a desenvolver.
- `oferta_formativa`: notícias, páginas de cursos e capacitações indicam uma resposta já existente, que pode reduzir ou cobrir parcialmente uma lacuna, mas não prova sozinha que a lacuna exista.

Sem essa separação, o relatório poderia cometer dois erros: tratar toda norma como evidência de lacuna ou tratar toda oferta de curso como prova de que há demanda não atendida. A metodologia escolhida evita esses atalhos.

### 3.2. Por que o corpus original foi expandido

A primeira linha de base era tecnicamente consistente, mas estreita: partia de uma página específica de Pesquisas Judiciárias e privilegiava relatórios de pesquisa. Esse recorte era adequado para um piloto, mas insuficiente para uma leitura ampla da agenda de capacitação do CNJ. Por isso, o universo documental foi ampliado para incluir atos normativos, páginas de programas, publicações, notícias, ofertas formativas e fontes associadas ao CNJ.

Na execução atual, o corpus analisável contém `{len(corpus)}` documentos e {_evidence_axis_note(evidence)} consideradas. A distribuição por tipo de fonte é:

{_markdown_table(source_counts, [("fonte_tipo", "Tipo de fonte"), ("documentos", "Documentos")], limit=12)}

### 3.3. Unidade de análise

A unidade primária de análise é o trecho textual rastreável. Para PDFs, o trecho preserva documento, página, URL, `doc_id`, hash e metadados do catálogo. Para HTML, o trecho preserva URL, tipo de fonte, origem da descoberta e texto extraído da página. O uso do trecho como unidade permite citar evidências, revisar falsos positivos e auditar a decisão sem depender de uma interpretação global opaca do documento.

O pipeline gera segmentos por página, parágrafo e janela deslizante. A detecção prioriza janelas textuais porque elas capturam coocorrências que podem ficar separadas artificialmente por quebras de página, cabeçalhos, tabelas ou parágrafos curtos. Essa escolha aumenta sensibilidade, mas também exige alertas de risco e calibração amostral para reduzir ambiguidade.

### 3.4. Descoberta, extração e rastreabilidade

O método usa descoberta multibase a partir de fontes configuradas em `config/sources.yml`. Cada item recebe `fonte_tipo`, `peso_fonte`, `forca_probatoria` e `uso_metodologico`. Esses campos tornam explícita a diferença entre diagnóstico, norma, guia, notícia, curso e painel.

O fluxo operacional é:

1. Descobrir fontes e links relacionados nos domínios CNJ permitidos.
2. Classificar cada item por tipo de fonte e uso metodológico.
3. Extrair texto de PDFs e HTML quando houver conteúdo analisável.
4. Segmentar o texto com identificadores estáveis.
5. Aplicar critérios lexicais e contextuais de lacuna, competência requerida e oferta formativa.
6. Priorizar evidências por score composto, recorrência, distribuição documental e valor institucional.
7. Gerar matrizes de lacunas, competências normativas, oferta versus lacuna e dossiê de evidências.

{_search_strings_section(context)}

### 3.7. Regras de detecção

A detecção combina grupos de termos e contexto. Termos de lacuna direta recebem maior peso; sinais formativos, problemas organizacionais, tecnologia/dados, inclusão, competência requerida, oferta formativa e implementação de política entram como camadas complementares. A classificação automática não decide sozinha a validade institucional do achado: ela identifica candidatos, explica quais termos acionaram a regra e registra o tipo de evidência.

As classes observadas nesta execução foram:

{_markdown_table(class_counts, [("achado_classe", "Classe de achado"), ("evidencias", "Evidências"), ("documentos", "Documentos")], limit=10)}

### 3.8. Priorização e score composto

A priorização usa o score composto:

`score_final = 0,45 * score_textual_norm + 0,30 * consistencia_evidencial + 0,25 * valor_institucional`

- `score_textual_norm`: mede a intensidade lexical e contextual do trecho, limitada a 1,0 e ponderada pelo peso da fonte.
- `consistencia_evidencial`: mede se o eixo aparece de forma recorrente e distribuída em documentos distintos.
- `valor_institucional`: representa relevância estratégica configurada por eixo temático.
- faixas de decisão: alta (`>= 0,75`), média (`>= 0,50`) e baixa (`< 0,50`).

O score textual bruto utiliza escala própria de detecção lexical; o score final é normalizado entre 0 e 1 após ponderação por consistência evidencial e valor institucional. Essa distinção evita comparar diretamente números que pertencem a escalas diferentes.

O score não é uma medida absoluta de urgência pedagógica. Ele é um instrumento de ordenação para decidir onde aprofundar a análise humana. Esse ponto é central: o método não transforma contagem de menções em decisão de curso; ele transforma evidência documental em uma fila priorizada de investigação.

### 3.9. Justificativa da escolha metodológica

Foram rejeitadas duas alternativas extremas. A primeira seria revisar manualmente todo o universo documental antes de qualquer síntese. Embora rigorosa, essa alternativa é lenta, cara e pouco escalável para ciclos periódicos de planejamento. A segunda seria usar apenas automação lexical e publicar os resultados como conclusão. Essa alternativa é rápida, mas frágil, porque termos como "capacitação", "desafio" ou "competência" podem ter sentidos muito diferentes conforme a fonte.

A escolha adotada é intermediária e mais defensável: automação rastreável para ampliar cobertura, pesos por tipo de fonte para reduzir viés, score composto para ordenar prioridades, alertas de risco para explicitar incerteza e calibração amostral para orientar revisão humana. Assim, o trabalho ganha escala sem abrir mão de auditabilidade.

### 3.10. Estado da calibração

{calibration['descricao']} A ausência de decisões revisadas não invalida a publicação técnica, mas limita seu uso: ela deve orientar uma etapa seguinte de análise robusta, e não ser tratada como validação institucional conclusiva.
"""


def _robust_gap_plan_section(
    matrix: pd.DataFrame,
    offer_gap: pd.DataFrame,
    source_matrix: pd.DataFrame,
    normative_matrix: pd.DataFrame,
) -> str:
    top_axes = matrix.head(7).copy() if not matrix.empty else pd.DataFrame()
    top_axes_table = _markdown_table(
        top_axes,
        [
            ("proposta", "Eixo/proposta"),
            ("evidencias_total", "Evidencias"),
            ("documentos_impactados", "Documentos"),
            ("score_final", "Score final"),
            ("faixa_prioridade", "Faixa"),
        ],
        limit=7,
    )
    offer_gap_top = _offer_gap_display(offer_gap).head(10).copy() if not offer_gap.empty else pd.DataFrame()
    source_focus = source_matrix.head(10).copy() if not source_matrix.empty else pd.DataFrame()
    normative_focus = normative_matrix.head(8).copy() if not normative_matrix.empty else pd.DataFrame()
    return f"""### 9.1. Objetivo do plano

O objetivo da próxima etapa não é produzir imediatamente uma grade de cursos. O objetivo é transformar os sinais documentais priorizados em um diagnóstico robusto de gaps, capaz de responder a quatro perguntas:

1. Qual é exatamente a lacuna: conhecimento, habilidade, atitude, processo, tecnologia, governança, padronização ou capacidade institucional?
2. Quem é afetado: magistrados, servidores, gestores, equipes técnicas, escolas judiciais, unidades de atendimento ou áreas de tecnologia?
3. A lacuna já possui resposta formativa ou normativa mapeada?
4. Qual intervenção é mais adequada: curso, trilha, oficina, guia, mentoria, laboratório, comunidade de prática, protocolo ou apoio à implementação?

### 9.2. Eixos que devem abrir o aprofundamento

Os primeiros eixos a aprofundar são aqueles com maior combinação de volume documental, distribuição em documentos distintos e valor institucional:

{top_axes_table}

### 9.3. Leitura oferta versus lacuna

O mapa de oferta versus lacuna evita propor capacitações redundantes. Quando há muitos gaps e poucas ofertas, a prioridade é o desenho de nova resposta. Quando há gaps e ofertas ao mesmo tempo, a prioridade é avaliar adequação, cobertura e efetividade da oferta existente.

O eixo `nao_classificado` reúne evidências com sinais de lacuna ou oferta que não atingiram aderência suficiente aos eixos temáticos predefinidos. Na próxima etapa, essas evidências devem ser revisadas para reclassificação, descarte ou eventual criação de novo eixo.

{_markdown_table(offer_gap_top, [("eixo", "Eixo"), ("gaps_observados", "Gaps"), ("competencias_requeridas", "Competências"), ("ofertas_formativas", "Ofertas"), ("leitura_interpretativa", "Leitura")], limit=10)}

### 9.4. Etapa 1 - Curadoria qualificada da evidência

Selecionar uma amostra dirigida, não aleatória simples, combinando:

- as 30 evidências de maior score por eixo prioritário;
- todas as evidências que entraram no dossiê final;
- evidências oriundas de atos normativos classificadas como `competencia_requerida`;
- evidências de notícia e oferta formativa, para confirmar se são contexto, demanda ou resposta existente;
- trechos de baixo score que aparecem em muitos documentos, pois podem indicar linguagem institucional recorrente mas ambígua.

Cada evidência deve receber decisão: `confirmar gap`, `confirmar competencia requerida`, `confirmar oferta existente`, `reclassificar`, `descartar` ou `pedir leitura de documento completo`.

### 9.5. Etapa 2 - Triangulação por tipo de fonte

Para cada eixo prioritário, cruzar três matrizes:

- diagnósticos e relatórios que apontam problemas observados;
- normas, guias e programas que estabelecem competências ou obrigações;
- cursos, capacitações e notícias que indicam resposta formativa existente.

Essa triangulação permite separar quatro situações:

- `gap forte`: problema observado em relatório e competência exigida por norma, sem oferta suficiente mapeada.
- `gap com resposta parcial`: problema observado e oferta existente, mas ainda com evidência de dificuldade ou baixa cobertura.
- `competencia normativa sem diagnostico`: norma exige capacidade, mas o corpus ainda não demonstra lacuna empírica.
- `oferta sem gap demonstrado`: há curso ou notícia, mas sem evidência suficiente de necessidade não atendida.

### 9.6. Etapa 3 - Tradução pedagógica dos gaps

Cada gap confirmado deve ser convertido em ficha pedagógica contendo:

- descrição do gap em linguagem institucional;
- evidências documentais principais;
- público-alvo provável;
- competência central a desenvolver;
- tipo de resposta recomendado;
- carga de esforço estimada;
- indicadores de resultado;
- riscos de implementação;
- dependência normativa ou tecnológica.

Essa ficha é o ponto de passagem entre pesquisa documental e desenho de oferta educacional.

### 9.7. Etapa 4 - Validação institucional

Submeter as fichas a um ciclo curto de validação com ENAJU, escolas judiciais e áreas técnicas relacionadas ao eixo. A validação deve perguntar se o gap é reconhecível, se já há iniciativas equivalentes, qual público deve ser priorizado e que tipo de resposta tem maior chance de adesão.

### 9.8. Entregáveis da análise robusta

Ao final da etapa seguinte, produzir:

- matriz revisada de gaps confirmados;
- mapa de competências requeridas por eixo;
- mapa de oferta existente versus gap;
- dossiê de evidências validadas;
- fichas pedagógicas por gap prioritário;
- plano de intervenção formativa com ondas de implementação;
- critérios de monitoramento e avaliação.

### 9.9. Foco documental para a próxima rodada

As fontes que mais devem orientar a revisão qualificada são:

{_markdown_table(source_focus, [("fonte_tipo", "Tipo de fonte"), ("achado_classe", "Classe"), ("eixo", "Eixo"), ("evidencias", "Evidências"), ("documentos", "Documentos")], limit=10)}

As competências normativas mais relevantes para leitura dirigida são:

{_markdown_table(normative_focus, [("eixo", "Eixo"), ("hipotese_competencia", "Competência"), ("fonte_tipo", "Fonte"), ("evidencias", "Evidências"), ("documentos", "Documentos")], limit=8)}

### 9.10. Critério de encerramento

Um gap só deve virar proposta de plano formativo quando cumprir pelo menos três critérios: evidência documental rastreável, interpretação confirmada por curadoria, público-alvo plausível, relação clara com competência ou capacidade institucional, e ausência ou insuficiência demonstrada de oferta equivalente. Esse critério reduz o risco de converter todo problema organizacional em curso e preserva a qualidade da recomendação final.
"""


def _expansion_section(
    corpus: pd.DataFrame,
    source_matrix: pd.DataFrame,
    normative_matrix: pd.DataFrame,
    offer_gap: pd.DataFrame,
) -> str:
    if "corpus_origem" not in corpus.columns and source_matrix.empty and offer_gap.empty:
        return "A publicação usa a linha de base exploratória original. A expansão multibase ainda não foi executada para este ciclo."
    origin_table = (
        corpus.groupby(["corpus_origem", "fonte_tipo"], dropna=False)
        .agg(documentos=("doc_id", "nunique"))
        .reset_index()
        .sort_values("documentos", ascending=False)
    ) if {"corpus_origem", "fonte_tipo", "doc_id"}.issubset(corpus.columns) else pd.DataFrame()
    return "\n\n".join(
        [
            "O corpus expandido separa documentos de diagnóstico, atos normativos, guias/manuais, notícias e ofertas formativas. Essa separação evita que comunicação institucional ou oferta de curso tenha o mesmo peso probatório de pesquisa ou diagnóstico.",
            "### Distribuição por origem e tipo de fonte",
            _markdown_table(origin_table, [("corpus_origem", "Origem"), ("fonte_tipo", "Tipo de fonte"), ("documentos", "Documentos")], limit=12),
            "### Lacunas por tipo de fonte",
            _markdown_table(source_matrix, [("fonte_tipo", "Tipo de fonte"), ("achado_classe", "Classe"), ("eixo", "Eixo"), ("evidencias", "Evidências"), ("documentos", "Documentos")], limit=12),
            "### Competências requeridas por normas, guias e programas",
            _markdown_table(normative_matrix, [("eixo", "Eixo"), ("hipotese_competencia", "Competência"), ("fonte_tipo", "Fonte"), ("evidencias", "Evidências"), ("documentos", "Documentos")], limit=10),
            "### Mapa oferta versus lacuna",
            "A coluna de leitura estratégica diferencia lacunas fortes com oferta parcial, lacunas sem oferta mapeada, competências normativas sem diagnóstico, ofertas sem gap demonstrado e evidências que ainda exigem revisão temática.",
            _markdown_table(_offer_gap_display(offer_gap), [("eixo", "Eixo"), ("gaps_observados", "Gaps"), ("competencias_requeridas", "Competências"), ("ofertas_formativas", "Ofertas"), ("leitura_interpretativa", "Leitura")], limit=10),
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
            ("publico_prioritario", "Público"),
            ("competencias_centrais", "Competências"),
            ("produto_esperado", "Produto esperado"),
            ("indicador_avaliacao", "Indicador"),
        ],
    )
    return f"""# Portfólio Preliminar de Capacitações e Trilhas Baseado em Evidências do CNJ

## Objetivo

Consolidar as lacunas priorizadas da linha de base `{context.run_id}` em uma proposta inicial de capacitações e trilhas para a ENAJU e escolas judiciais.

## Status

**{status_label}**

## Portfólio preliminar para validação

{portfolio_table}

## Critérios de priorização

- score textual do trecho;
- consistência evidencial por recorrência e documentos distintos;
- valor institucional configurado por eixo;
- rebaixamento de itens sem classificação temática;
- leitura final condicionada a validação pedagógica e institucional.

## Magnitude documental

{_markdown_table(matrix, [("proposta", "Proposta"), ("evidencias_total", "Evidências"), ("documentos_impactados", "Documentos"), ("score_final", "Score final")], limit=10)}
"""
