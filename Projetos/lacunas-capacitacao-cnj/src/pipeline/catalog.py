from __future__ import annotations

import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urljoin, urlsplit

import pandas as pd
from bs4 import BeautifulSoup, Tag
from rapidfuzz.fuzz import ratio

from .common import (
    RunContext,
    TARGET_SECTIONS,
    json_dumps,
    normalize_text,
    normalize_url,
    read_csv,
    sha256_bytes,
    slugify,
    stable_id,
    utc_now,
    write_csv,
)

LOGGER = logging.getLogger(__name__)
YEAR_PATTERN = re.compile(r"(?<!\d)(20\d{2})(?!\d)")
UPLOAD_YEAR_PATTERN = re.compile(r"/wp-content/uploads/(20\d{2})/")


@dataclass
class Card:
    section: str
    card_id: str
    title: str
    description: str
    dom_order: int
    links: list[dict[str, str]]


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _resource_type(url: str) -> str:
    path = urlsplit(url).path.casefold()
    if path.endswith(".pdf"):
        return "pdf"
    if path.endswith(".zip"):
        return "base_de_dados"
    if "painel" in normalize_text(url) or "dashboard" in normalize_text(url):
        return "painel"
    return "pagina_web"


def _closest_card(heading: Tag) -> Tag | None:
    for parent in heading.parents:
        if parent.name == "section" and parent.get("data-element_type") == "section":
            return parent
    return None


def extract_editorial_cards(
    html: bytes | str, base_url: str, target_sections: list[str] | None = None
) -> list[Card]:
    soup = BeautifulSoup(html, "html.parser")
    configured_sections = target_sections or list(TARGET_SECTIONS.values())
    section_lookup = {normalize_text(section): section for section in configured_sections}
    cards: list[Card] = []
    seen_cards: set[str] = set()
    dom_order = 0
    for heading in soup.find_all("h2"):
        section_key = normalize_text(heading.get_text(" ", strip=True))
        if section_key not in section_lookup:
            continue
        section_name = section_lookup[section_key]
        for h4 in heading.find_all_next("h4"):
            if h4.find_previous("h2") is not heading:
                break
            card_node = _closest_card(h4)
            if card_node is None:
                continue
            card_id = card_node.get("data-id") or stable_id("card", section_name, str(card_node))
            if card_id in seen_cards:
                continue
            seen_cards.add(card_id)
            dom_order += 1
            title = _clean(h4.get_text(" ", strip=True))
            description = _clean(" ".join(p.get_text(" ", strip=True) for p in card_node.find_all("p")))
            links: list[dict[str, str]] = []
            for anchor in card_node.find_all("a", href=True):
                url = urljoin(base_url, anchor["href"].strip())
                links.append(
                    {
                        "url": url,
                        "url_normalizada": normalize_url(url),
                        "texto_ancora": _clean(anchor.get_text(" ", strip=True)),
                        "tipo_recurso": _resource_type(url),
                    }
                )
            cards.append(
                Card(
                    section=section_name,
                    card_id=card_id,
                    title=title,
                    description=description,
                    dom_order=dom_order,
                    links=links,
                )
            )
    return cards


def _extract_upload_year(url: str) -> int | None:
    match = UPLOAD_YEAR_PATTERN.search(url)
    return int(match.group(1)) if match else None


def _extract_document_year(card_title: str, label: str, filename: str) -> int | None:
    for value in (label, card_title, filename):
        years = YEAR_PATTERN.findall(value)
        if years:
            return int(years[-1])
    return None


def _infer_language(filename: str, label: str) -> str:
    haystack = normalize_text(f"{filename} {label}")
    if any(term in haystack for term in ("justice in numbers", "numbers in justice", "english")):
        return "en"
    if any(term in haystack for term in ("justicia", "cifras", "espanol")):
        return "es"
    return "pt"


def _infer_document_type(filename: str, label: str, title: str) -> str:
    haystack = normalize_text(f"{filename} {label} {title}")
    if "sumario" in haystack:
        return "sumario"
    if "apresentacao" in haystack:
        return "apresentacao"
    if "diagnostico" in haystack:
        return "diagnostico"
    if "pesquisa" in haystack or "censo" in haystack:
        return "pesquisa"
    if any(term in haystack for term in ("relatorio", "balanco", "justica em numeros")):
        return "relatorio"
    return "outro"


def _family_seed(title: str) -> str:
    seed = normalize_text(title)
    removable = (
        "sumario executivo",
        "sumario",
        "relatorio",
        "diagnostico",
        "pesquisa",
        "apresentacao",
        "versao completa",
    )
    for term in removable:
        seed = seed.replace(term, " ")
    seed = re.sub(r"\s+", " ", seed).strip()
    return seed or normalize_text(title)


def _assign_families(records: list[dict[str, Any]], minimum_similarity: int) -> None:
    seeds: list[tuple[str, str]] = []
    for record in records:
        seed = _family_seed(record["titulo_inferido"])
        matched_family = ""
        for existing_seed, family_id in seeds:
            seed_years = set(YEAR_PATTERN.findall(seed))
            existing_years = set(YEAR_PATTERN.findall(existing_seed))
            if seed_years and existing_years and seed_years != existing_years:
                continue
            if ratio(seed, existing_seed) >= minimum_similarity:
                matched_family = family_id
                break
        if not matched_family:
            matched_family = stable_id("fam", seed)
            seeds.append((seed, matched_family))
        record["familia_documental_id"] = matched_family
        record["familia_seed"] = seed


def _choose_principal(records: Iterable[dict[str, Any]]) -> dict[str, Any] | None:
    preferred = [
        record
        for record in records
        if record["idioma_inferido"] == "pt"
        and record["tipo_documento"] not in {"sumario", "apresentacao"}
    ]
    if not preferred:
        return None
    return sorted(preferred, key=lambda row: (row["tipo_documento"] == "outro", row["doc_id"]))[0]


def _apply_relations_and_status(
    records: list[dict[str, Any]], start_year: int, end_year: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    families: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        families[record["familia_documental_id"]].append(record)

    relations: list[dict[str, Any]] = []
    for family_records in families.values():
        principal = _choose_principal(family_records)
        for record in family_records:
            reasons: list[str] = []
            status = "incluir"
            upload_year = record["ano_url"]
            if upload_year is None or not start_year <= upload_year <= end_year:
                status = "excluir"
                reasons.append("fora_janela_temporal")
            if principal and record["doc_id"] != principal["doc_id"]:
                relation_type = ""
                if record["idioma_inferido"] in {"en", "es"}:
                    relation_type = "traducao_de"
                    status = "excluir"
                    reasons.append("traducao_com_original_portugues")
                elif record["tipo_documento"] == "sumario":
                    relation_type = "sumario_de"
                    status = "excluir"
                    reasons.append("sumario_com_versao_completa")
                elif record["tipo_documento"] == "apresentacao":
                    relation_type = "apresentacao_de"
                    status = "excluir"
                    reasons.append("apresentacao_relacionada")
                if relation_type:
                    relations.append(
                        {
                            "doc_id_origem": record["doc_id"],
                            "doc_id_destino": principal["doc_id"],
                            "tipo_relacao": relation_type,
                            "metodo": "familia_documental",
                            "confianca": 1.0,
                            "revisado_humano": False,
                        }
                    )
            elif record["tipo_documento"] == "apresentacao":
                status = "excluir"
                reasons.append("apresentacao_sem_relatorio_principal")
            if not reasons:
                reasons.append("documento_principal_portugues")
            record["status_corpus"] = status
            record["motivo_status"] = ";".join(reasons)
            divergence = (
                record["ano_url"] is not None
                and record["ano_documento"] is not None
                and record["ano_url"] != record["ano_documento"]
            )
            record["revisao_catalogo_pendente"] = bool(
                divergence
                or record["tipo_documento"] in {"sumario", "apresentacao"}
                or record["idioma_inferido"] in {"en", "es"}
                or record["tipo_documento"] == "outro"
            )
    return records, relations


def build_catalog(context: RunContext) -> dict[str, int]:
    if not context.snapshot_html.exists():
        raise FileNotFoundError("Execute a etapa snapshot antes de catalogar.")
    snapshot = json.loads(context.snapshot_metadata.read_text(encoding="utf-8"))
    html = context.snapshot_html.read_bytes()
    config = context.pipeline_config
    start_year = int(config["fonte"]["ano_inicial"])
    end_year = int(context.as_of[:4])
    cards = extract_editorial_cards(
        html,
        config["fonte"]["url"],
        target_sections=config["fonte"]["secoes_editoriais"],
    )
    records_by_url: dict[str, dict[str, Any]] = {}
    resource_rows: list[dict[str, Any]] = []
    collected_at = utc_now()

    for card in cards:
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for link in card.links:
            grouped[link["url_normalizada"]].append(link)
        for normalized_url, occurrences in grouped.items():
            first = occurrences[0]
            labels = sorted({item["texto_ancora"] for item in occurrences if item["texto_ancora"]})
            longest_label = max(labels, key=len, default="")
            resource_type = first["tipo_recurso"]
            common = {
                "run_id": context.run_id,
                "as_of": context.as_of,
                "snapshot_sha256": snapshot["snapshot_sha256"],
                "url": first["url"],
                "url_normalizada": normalized_url,
                "texto_ancora": longest_label,
                "textos_ancora": json_dumps(labels),
                "secao_portal": card.section,
                "prioridade_analitica": "nucleo" if card.section == "Producao Interna" else "complementar",
                "card_id": card.card_id,
                "card_ordem_dom": card.dom_order,
                "titulo_card": card.title,
                "descricao_card": card.description,
                "ocorrencias_html": len(occurrences),
                "coletado_em": collected_at,
            }
            if resource_type != "pdf":
                resource_rows.append({**common, "tipo_recurso": resource_type})
                continue
            filename = Path(urlsplit(first["url"]).path).name
            doc_id = stable_id("doc", normalized_url)
            record = {
                **common,
                "doc_id": doc_id,
                "nome_arquivo": filename,
                "ano_url": _extract_upload_year(first["url"]),
                "ano_documento": _extract_document_year(card.title, longest_label, filename),
                "ano_referencia": _extract_document_year(card.title, longest_label, filename),
                "titulo_inferido": card.title or longest_label or filename,
                "categoria_inferida": card.section,
                "idioma_inferido": _infer_language(filename, longest_label),
                "tipo_documento": _infer_document_type(filename, longest_label, card.title),
            }
            if normalized_url in records_by_url:
                previous = records_by_url[normalized_url]
                previous["ocorrencias_html"] += record["ocorrencias_html"]
                previous["textos_ancora"] = json_dumps(
                    sorted(
                        set(json.loads(previous["textos_ancora"]))
                        | set(json.loads(record["textos_ancora"]))
                    )
                )
            else:
                records_by_url[normalized_url] = record

    records = list(records_by_url.values())
    _assign_families(records, int(config["deduplicacao"]["similaridade_titulo_minima"]))
    records, relations = _apply_relations_and_status(records, start_year, end_year)
    raw_path = context.paths.processed / "catalogo_pdfs_bruto.csv"
    catalog_path = context.paths.processed / "catalogo_pdfs.csv"
    relation_path = context.paths.processed / "relacoes_documentos.csv"
    resources_path = context.paths.processed / "recursos_relacionados.csv"
    review_path = context.paths.processed / "fila_curadoria_catalogo.csv"
    approved_path = context.paths.processed / "catalogo_pdfs_aprovado.csv"
    write_csv(records, raw_path)
    write_csv(records, catalog_path)
    write_csv(relations, relation_path)
    write_csv(resource_rows, resources_path)
    review_rows = [
        record
        for record in records
        if record["revisao_catalogo_pendente"]
        and record["ano_url"] is not None
        and start_year <= record["ano_url"] <= end_year
    ]
    write_csv(review_rows, review_path)
    write_csv([record for record in records if record["status_corpus"] == "incluir"], approved_path)
    summary = {
        "cards_editoriais": len(cards),
        "pdfs_catalogados": len(records),
        "pdfs_na_janela": sum(
            record["ano_url"] is not None and start_year <= record["ano_url"] <= end_year
            for record in records
        ),
        "pdfs_incluir_provisorio": sum(record["status_corpus"] == "incluir" for record in records),
        "pdfs_excluir": sum(record["status_corpus"] == "excluir" for record in records),
        "itens_curadoria_catalogo": len(review_rows),
        "recursos_relacionados": len(resource_rows),
        "relacoes_documentais": len(relations),
    }
    context.update_manifest("catalog", **summary)
    LOGGER.info("Catalogo gerado: %s", summary)
    return summary


def import_catalog_review(context: RunContext, review_file: Path) -> dict[str, int]:
    catalog = read_csv(context.paths.processed / "catalogo_pdfs.csv")
    review = read_csv(review_file)
    required = {"doc_id", "status_corpus", "motivo_status"}
    missing = required - set(review.columns)
    if missing:
        raise ValueError(f"Curadoria de catalogo sem colunas obrigatorias: {sorted(missing)}")
    updated = catalog.set_index("doc_id")
    for row in review.to_dict("records"):
        if row["doc_id"] not in updated.index:
            raise ValueError(f"doc_id desconhecido na curadoria: {row['doc_id']}")
        updated.at[row["doc_id"], "status_corpus"] = row["status_corpus"]
        updated.at[row["doc_id"], "motivo_status"] = row["motivo_status"]
        updated.at[row["doc_id"], "revisao_catalogo_pendente"] = False
    updated = updated.reset_index()
    write_csv(updated, context.paths.processed / "catalogo_pdfs.csv")
    approved = updated[updated["status_corpus"] == "incluir"].copy()
    write_csv(approved, context.paths.processed / "catalogo_pdfs_aprovado.csv")
    summary = {"catalogo_aprovado": len(approved), "decisoes_importadas": len(review)}
    context.update_manifest("catalog-review", **summary)
    return summary
