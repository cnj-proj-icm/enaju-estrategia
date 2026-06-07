from __future__ import annotations

import logging
import re
from collections import deque
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

import pandas as pd
import requests
from bs4 import BeautifulSoup

from .common import (
    RunContext,
    json_dumps,
    normalize_text,
    normalize_url,
    sha256_bytes,
    slugify,
    stable_id,
    utc_now,
    write_csv,
    write_parquet,
)
from .corpus import _segment_row, _window_segments
from .sources import enabled_sources

LOGGER = logging.getLogger(__name__)

DISCOVERY_TERMS = (
    "capacitacao",
    "capacitações",
    "capacitação",
    "competencia",
    "competência",
    "formacao",
    "formação",
    "treinamento",
    "curso",
    "relatorio",
    "relatório",
    "diagnostico",
    "diagnóstico",
    "pesquisa",
    "manual",
    "guia",
    "cartilha",
    "publicacao",
    "publicação",
    "publicacoes",
    "publicações",
    "normativo",
    "normativos",
    "resolucao",
    "resolução",
    "portaria",
    "recomendacao",
    "recomendação",
    "noticia",
    "notícia",
    "noticias",
    "notícias",
    "implementacao",
    "implementação",
    "politica",
    "política",
)

SOURCE_POLICIES = {
    "relatorio_diagnostico_pesquisa": ("alta", 1.00, "gap_observado"),
    "ato_normativo": ("alta_normativa", 0.85, "competencia_requerida"),
    "manual_guia_cartilha": ("media", 0.70, "competencia_requerida"),
    "noticia_cnj": ("contextual", 0.45, "evidencia_contextual"),
    "oferta_formativa": ("oferta", 0.40, "oferta_formativa"),
    "pagina_programa": ("contextual", 0.60, "competencia_requerida"),
    "painel_dados": ("metadado", 0.30, "metadado"),
    "base_dados": ("metadado", 0.30, "metadado"),
}


def _expansion_config(context: RunContext) -> dict[str, Any]:
    config = context.pipeline_config.get("expansao_corpus", {})
    return {
        "ano_inicial": int(config.get("ano_inicial", 2021)),
        "ano_final": int(context.as_of[:4]),
        "max_pages": int(config.get("max_pages", 120)),
        "max_depth": int(config.get("max_depth", 1)),
        "max_links_per_page": int(config.get("max_links_per_page", 80)),
        "min_chars_html": int(config.get("min_chars_html", 300)),
        "allowed_domains": config.get(
            "allowed_domains",
            ["cnj.jus.br", "atos.cnj.jus.br", "bibliotecadigital.cnj.jus.br"],
        ),
    }


def _allowed_url(url: str, domains: list[str]) -> bool:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    host = parsed.netloc.casefold()
    return any(host == domain or host.endswith(f".{domain}") for domain in domains)


def _resource_type(url: str) -> str:
    path = urlsplit(url).path.casefold()
    normalized = normalize_text(url)
    if path.endswith(".pdf"):
        return "pdf"
    if path.endswith(".zip") or "base-de-dados" in normalized or "base de dados" in normalized:
        return "base_de_dados"
    if any(term in normalized for term in ("painel", "dashboard", "paineisanalytics")):
        return "painel"
    return "html"


def _extract_year(*values: Any) -> int | None:
    for value in values:
        years = re.findall(r"(?<!\d)(20\d{2})(?!\d)", str(value or ""))
        if years:
            return int(years[-1])
    return None


def _matched_discovery_terms(*values: Any) -> list[str]:
    haystack = normalize_text(" ".join(str(value or "") for value in values))
    return sorted({normalize_text(term) for term in DISCOVERY_TERMS if normalize_text(term) in haystack})


def classify_source_item(url: str, label: str, seed: dict[str, Any], title: str = "") -> dict[str, Any]:
    haystack = normalize_text(f"{url} {label} {title} {seed.get('name', '')} {seed.get('section', '')}")
    seed_type = str(seed.get("type", "")).strip()
    resource_type = _resource_type(url)
    if resource_type == "painel":
        source_type = "painel_dados"
    elif resource_type == "base_de_dados":
        source_type = "base_dados"
    elif seed_type == "normative_acts" or "atos.cnj.jus.br" in urlsplit(url).netloc.casefold() or any(
        term in haystack for term in ("resolucao", "portaria", "provimento", "recomendacao", "instrucao normativa")
    ):
        source_type = "ato_normativo"
    elif seed_type == "news" or "/noticia" in haystack or "noticias" in haystack:
        source_type = "noticia_cnj"
    elif seed_type in {"training", "justice_4_training"} or any(
        term in haystack for term in ("curso", "capacitacao", "webinar", "autoinstrucional", "ead")
    ):
        source_type = "oferta_formativa"
    elif any(term in haystack for term in ("manual", "guia", "cartilha", "protocolo", "orientacoes")):
        source_type = "manual_guia_cartilha"
    elif any(term in haystack for term in ("relatorio", "diagnostico", "pesquisa", "censo", "justica em numeros")):
        source_type = "relatorio_diagnostico_pesquisa"
    else:
        source_type = "pagina_programa" if seed_type in {"program", "publications", "digital_library"} else "relatorio_diagnostico_pesquisa"
    force, weight, use = SOURCE_POLICIES[source_type]
    return {
        "fonte_tipo": source_type,
        "forca_probatoria": force,
        "peso_fonte": weight,
        "uso_metodologico": use,
        "tipo_recurso": resource_type,
    }


def _html_title(soup: BeautifulSoup) -> str:
    if soup.find("h1"):
        return soup.find("h1").get_text(" ", strip=True)
    if soup.title:
        return soup.title.get_text(" ", strip=True)
    return ""


def _main_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "svg", "form"]):
        tag.decompose()
    candidates = soup.select("main, article, .entry-content, .post-content, .elementor-widget-theme-post-content")
    node = candidates[0] if candidates else soup.body or soup
    text = node.get_text("\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _raw_html_path(context: RunContext, doc_id: str) -> Path:
    path = context.paths.raw_html / "expanded"
    path.mkdir(parents=True, exist_ok=True)
    return path / f"{doc_id}.html"


def _text_path(context: RunContext, doc_id: str) -> Path:
    path = context.paths.text_clean / "expanded"
    path.mkdir(parents=True, exist_ok=True)
    return path / f"{doc_id}.txt"


def _seed_priority(seed: dict[str, Any]) -> str:
    priority = str(seed.get("priority", "medium")).strip().lower()
    if priority == "high":
        return "nucleo_expandido"
    if priority == "medium":
        return "complementar_expandido"
    return "contextual_expandido"


def _row_for_item(
    context: RunContext,
    url: str,
    seed: dict[str, Any],
    label: str,
    depth: int,
    discovered_from: str,
    title: str = "",
) -> dict[str, Any]:
    normalized = normalize_url(url)
    doc_id = stable_id("src", normalized)
    classification = classify_source_item(url, label, seed, title)
    year = _extract_year(url, label, title)
    return {
        "run_id": context.run_id,
        "as_of": context.as_of,
        "doc_id": doc_id,
        "source_name": seed["name"],
        "source_url": seed["url"],
        "source_section": seed["section"],
        "url": url,
        "url_normalizada": normalized,
        "titulo": title or label or Path(urlsplit(url).path).name or seed["name"],
        "texto_ancora": label,
        "secao_portal": seed["section"],
        "prioridade_analitica": _seed_priority(seed),
        "ano_documento": year,
        "ano_url": _extract_year(url),
        "dominio": urlsplit(url).netloc.casefold(),
        "profundidade": depth,
        "descoberto_de": discovered_from,
        "termos_descoberta": json_dumps(_matched_discovery_terms(url, label, title)),
        "status_descoberta": "descoberto",
        "snapshot_sha256": "",
        "arquivo_html": "",
        "caracteres_texto": 0,
        "erro": "",
        "coletado_em": "",
        **classification,
    }


def discover_sources(context: RunContext, force: bool = False) -> dict[str, int]:
    config = _expansion_config(context)
    seeds = enabled_sources(context.paths.config / "sources.yml")
    queue: deque[tuple[str, dict[str, Any], int, str, str]] = deque()
    rows_by_url: dict[str, dict[str, Any]] = {}
    for seed in seeds:
        queue.append((seed["url"], seed, 0, "", seed["name"]))

    fetched_pages = 0
    session = requests.Session()
    timeout = int(context.pipeline_config["download"]["timeout_segundos"])
    while queue and fetched_pages < config["max_pages"]:
        url, seed, depth, parent, label = queue.popleft()
        normalized = normalize_url(url)
        if not _allowed_url(url, config["allowed_domains"]):
            continue
        row = rows_by_url.get(normalized) or _row_for_item(context, url, seed, label, depth, parent)
        rows_by_url[normalized] = row
        if row["tipo_recurso"] != "html":
            continue
        if row["status_descoberta"] == "coletado" and not force:
            continue
        try:
            response = session.get(url, timeout=timeout, headers={"User-Agent": "ENAJU-corpus-expandido/0.1"})
            row["http_status"] = response.status_code
            row["content_type"] = response.headers.get("content-type", "")
            response.raise_for_status()
            if "html" not in row["content_type"].casefold():
                row["status_descoberta"] = "metadado"
                continue
            content = response.content
            soup = BeautifulSoup(content, "html.parser")
            title = _html_title(soup)
            text = _main_text(soup)
            row.update(
                {
                    "titulo": title or row["titulo"],
                    "snapshot_sha256": sha256_bytes(content),
                    "arquivo_html": str(_raw_html_path(context, row["doc_id"]).relative_to(context.paths.root)),
                    "caracteres_texto": len(text),
                    "status_descoberta": "coletado",
                    "coletado_em": utc_now(),
                    "termos_descoberta": json_dumps(_matched_discovery_terms(url, label, title, text[:1000])),
                }
            )
            (context.paths.root / row["arquivo_html"]).write_bytes(content)
            fetched_pages += 1
            if depth >= config["max_depth"]:
                continue
            links_seen = 0
            for anchor in soup.find_all("a", href=True):
                if links_seen >= config["max_links_per_page"]:
                    break
                target = urljoin(url, anchor["href"].strip())
                if not _allowed_url(target, config["allowed_domains"]):
                    continue
                anchor_label = anchor.get_text(" ", strip=True)
                terms = _matched_discovery_terms(target, anchor_label)
                if _resource_type(target) == "html" and not terms:
                    continue
                links_seen += 1
                target_normalized = normalize_url(target)
                rows_by_url.setdefault(
                    target_normalized,
                    _row_for_item(context, target, seed, anchor_label, depth + 1, normalized),
                )
                if _resource_type(target) == "html" and target_normalized != normalized:
                    queue.append((target, seed, depth + 1, normalized, anchor_label))
        except Exception as exc:  # noqa: BLE001 - erro precisa ficar por fonte
            row["status_descoberta"] = "falha"
            row["erro"] = f"{type(exc).__name__}: {exc}"
            LOGGER.warning("Falha na descoberta %s: %s", url, row["erro"])

    catalog = pd.DataFrame(rows_by_url.values()).sort_values(["source_name", "profundidade", "url"])
    write_csv(catalog, context.paths.processed / "catalogo_fontes_expandido.csv")
    summary = {
        "fontes_configuradas": len(seeds),
        "itens_catalogados": len(catalog),
        "paginas_coletadas": int((catalog["status_descoberta"] == "coletado").sum()) if not catalog.empty else 0,
        "pdfs_descobertos": int((catalog["tipo_recurso"] == "pdf").sum()) if not catalog.empty else 0,
        "html_descobertos": int((catalog["tipo_recurso"] == "html").sum()) if not catalog.empty else 0,
    }
    context.update_manifest("discover-sources", **summary)
    return summary


def _baseline_corpus(context: RunContext) -> pd.DataFrame:
    path = context.paths.processed / "corpus_documentos.csv"
    if not path.exists():
        return pd.DataFrame()
    corpus = pd.read_csv(path, encoding="utf-8-sig", keep_default_na=False)
    if "fonte_tipo" not in corpus.columns:
        corpus["fonte_tipo"] = "relatorio_diagnostico_pesquisa"
    if "peso_fonte" not in corpus.columns:
        corpus["peso_fonte"] = 1.0
    corpus["peso_fonte"] = pd.to_numeric(corpus["peso_fonte"], errors="coerce").fillna(1.0)
    if "forca_probatoria" not in corpus.columns:
        corpus["forca_probatoria"] = "alta"
    if "uso_metodologico" not in corpus.columns:
        corpus["uso_metodologico"] = "gap_observado"
    corpus["corpus_origem"] = "baseline_pdf"
    return corpus


def _expanded_html_corpus(context: RunContext, catalog: pd.DataFrame) -> pd.DataFrame:
    config = _expansion_config(context)
    rows: list[dict[str, Any]] = []
    eligible = catalog[
        (catalog["tipo_recurso"] == "html")
        & (catalog["status_descoberta"] == "coletado")
        & (pd.to_numeric(catalog["caracteres_texto"], errors="coerce").fillna(0) >= config["min_chars_html"])
    ].copy()
    for item in eligible.to_dict("records"):
        html_path = context.paths.root / item["arquivo_html"]
        soup = BeautifulSoup(html_path.read_bytes(), "html.parser")
        text = _main_text(soup)
        text_path = _text_path(context, item["doc_id"])
        text_path.write_text(text, encoding="utf-8")
        rows.append(
            {
                "run_id": context.run_id,
                "as_of": context.as_of,
                "snapshot_sha256": item["snapshot_sha256"],
                "doc_id": item["doc_id"],
                "titulo": item["titulo"],
                "ano": item["ano_documento"],
                "ano_url": item["ano_url"],
                "url": item["url"],
                "secao_portal": item["secao_portal"],
                "prioridade_analitica": item["prioridade_analitica"],
                "tipo_documento": item["fonte_tipo"],
                "categoria": item["source_section"],
                "idioma": "pt",
                "sha256": item["snapshot_sha256"],
                "arquivo_txt_clean": str(text_path.relative_to(context.paths.root)),
                "paginas_total": 1,
                "incluido_em": utc_now(),
                "fonte_tipo": item["fonte_tipo"],
                "peso_fonte": item["peso_fonte"],
                "forca_probatoria": item["forca_probatoria"],
                "uso_metodologico": item["uso_metodologico"],
                "corpus_origem": "expanded_html",
            }
        )
    return pd.DataFrame(rows)


def build_expanded_corpus(context: RunContext) -> dict[str, int]:
    catalog_path = context.paths.processed / "catalogo_fontes_expandido.csv"
    if not catalog_path.exists():
        raise FileNotFoundError("Catalogo expandido ausente. Execute discover-sources primeiro.")
    catalog = pd.read_csv(catalog_path, encoding="utf-8-sig", keep_default_na=False)
    baseline = _baseline_corpus(context)
    html_corpus = _expanded_html_corpus(context, catalog)
    corpus = pd.concat([baseline, html_corpus], ignore_index=True, sort=False)
    if corpus.empty:
        corpus = pd.DataFrame(columns=["doc_id"])
    write_csv(corpus, context.paths.processed / "corpus_documentos_expandido.csv")
    parquet_corpus = corpus.copy()
    for column in parquet_corpus.columns:
        if parquet_corpus[column].dtype == "object":
            parquet_corpus[column] = parquet_corpus[column].astype(str)
    write_parquet(parquet_corpus, context.paths.processed / "corpus_documentos_expandido.parquet")

    segments = []
    baseline_segments = context.paths.processed / "segmentos.csv"
    if baseline_segments.exists() and not baseline.empty:
        base_segments = pd.read_csv(baseline_segments, encoding="utf-8-sig", keep_default_na=False)
        segments.append(base_segments)
    config = context.pipeline_config["segmentacao"]
    html_segment_rows: list[dict[str, Any]] = []
    for document in html_corpus.to_dict("records"):
        text = (context.paths.root / document["arquivo_txt_clean"]).read_text(encoding="utf-8")
        if not text.strip():
            continue
        html_segment_rows.append(_segment_row(document["doc_id"], 1, "pagina", 0, len(text), text))
        for start, end, window_text in _window_segments(
            text,
            int(config["janela_caracteres"]),
            int(config["sobreposicao_caracteres"]),
        ):
            html_segment_rows.append(_segment_row(document["doc_id"], 1, "janela", start, end, window_text))
    if html_segment_rows:
        segments.append(pd.DataFrame(html_segment_rows))
    segment_frame = pd.concat(segments, ignore_index=True, sort=False) if segments else pd.DataFrame()
    write_csv(segment_frame, context.paths.processed / "segmentos_expandido.csv")
    write_parquet(segment_frame, context.paths.processed / "segmentos_expandido.parquet")

    summary = {
        "documentos_baseline": len(baseline),
        "documentos_html_expandido": len(html_corpus),
        "documentos_corpus_expandido": len(corpus),
        "segmentos_expandido": len(segment_frame),
        "pdfs_pendentes": int((catalog["tipo_recurso"] == "pdf").sum()) if not catalog.empty else 0,
    }
    context.update_manifest("expanded-corpus", **summary)
    return summary
