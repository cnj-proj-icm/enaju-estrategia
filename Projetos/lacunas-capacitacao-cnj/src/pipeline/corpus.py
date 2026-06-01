from __future__ import annotations

import logging
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from .common import (
    PAGE_BREAK,
    RunContext,
    normalize_text,
    read_csv,
    sha256_bytes,
    stable_id,
    utc_now,
    write_csv,
    write_parquet,
)

LOGGER = logging.getLogger(__name__)


def _register_hash_duplicates(context: RunContext, downloads: pd.DataFrame) -> None:
    duplicates = downloads[downloads["status_download"] == "duplicata"]
    if duplicates.empty:
        return
    catalog_path = context.paths.processed / "catalogo_pdfs.csv"
    approved_path = context.paths.processed / "catalogo_pdfs_aprovado.csv"
    relations_path = context.paths.processed / "relacoes_documentos.csv"
    catalog = read_csv(catalog_path)
    relations = read_csv(relations_path) if relations_path.exists() else pd.DataFrame()
    relation_rows = relations.to_dict("records") if not relations.empty else []
    known = {
        (row.get("doc_id_origem"), row.get("doc_id_destino"), row.get("tipo_relacao"))
        for row in relation_rows
    }
    for duplicate in duplicates.to_dict("records"):
        mask = catalog["doc_id"] == duplicate["doc_id"]
        catalog.loc[mask, "status_corpus"] = "excluir"
        catalog.loc[mask, "motivo_status"] = "duplicata_sha256"
        key = (duplicate["doc_id"], duplicate["duplicata_de"], "duplicata_de")
        if key not in known:
            relation_rows.append(
                {
                    "doc_id_origem": duplicate["doc_id"],
                    "doc_id_destino": duplicate["duplicata_de"],
                    "tipo_relacao": "duplicata_de",
                    "metodo": "sha256",
                    "confianca": 1.0,
                    "revisado_humano": False,
                }
            )
    write_csv(catalog, catalog_path)
    write_csv(catalog[catalog["status_corpus"] == "incluir"], approved_path)
    write_csv(relation_rows, relations_path)


def download_pdfs(context: RunContext, force: bool = False) -> pd.DataFrame:
    source = context.paths.processed / "catalogo_pdfs_aprovado.csv"
    if not source.exists():
        raise FileNotFoundError("Catalogo aprovado ausente. Execute catalog primeiro.")
    catalog = read_csv(source)
    config = context.pipeline_config["download"]
    existing_path = context.paths.processed / "download_status.csv"
    existing = read_csv(existing_path) if existing_path.exists() else pd.DataFrame()
    existing_by_doc = {
        row["doc_id"]: row for row in existing.to_dict("records")
    } if not existing.empty else {}
    rows: list[dict[str, Any]] = []
    seen_hash: dict[str, str] = {}
    selected_doc_ids = set(catalog["doc_id"])
    for record in catalog.to_dict("records"):
        doc_id = record["doc_id"]
        target = context.paths.raw_pdf / f"{doc_id}.pdf"
        previous = existing_by_doc.get(doc_id)
        if previous and previous["status_download"] == "sucesso" and target.exists() and not force:
            rows.append(previous)
            if previous.get("sha256"):
                seen_hash[previous["sha256"]] = doc_id
            continue
        row = {
            "run_id": context.run_id,
            "as_of": context.as_of,
            "doc_id": doc_id,
            "url": record["url"],
            "arquivo_pdf": str(target.relative_to(context.paths.root)),
            "http_status": "",
            "content_type": "",
            "bytes": 0,
            "sha256": "",
            "duplicata_de": "",
            "status_download": "falha",
            "erro": "",
            "baixado_em": utc_now(),
        }
        error = ""
        for attempt in range(1, int(config["tentativas"]) + 1):
            try:
                response = requests.get(
                    record["url"],
                    timeout=int(config["timeout_segundos"]),
                    headers={"User-Agent": "ENAJU-lacunas-capacitacao-cnj/0.1"},
                )
                row["http_status"] = response.status_code
                row["content_type"] = response.headers.get("content-type", "")
                response.raise_for_status()
                content = response.content
                if config["validar_content_type"] and "pdf" not in row["content_type"].casefold():
                    LOGGER.warning(
                        "Content-Type inesperado para %s: %s; validando assinatura.",
                        doc_id,
                        row["content_type"],
                    )
                if config["validar_assinatura_pdf"] and not content.startswith(b"%PDF"):
                    raise ValueError("arquivo_sem_assinatura_pdf")
                digest = sha256_bytes(content)
                target.write_bytes(content)
                row["bytes"] = len(content)
                row["sha256"] = digest
                row["status_download"] = "sucesso"
                if digest in seen_hash:
                    row["duplicata_de"] = seen_hash[digest]
                    row["status_download"] = "duplicata"
                else:
                    seen_hash[digest] = doc_id
                error = ""
                break
            except Exception as exc:  # noqa: BLE001 - erro precisa ser persistido por item
                error = f"tentativa_{attempt}:{type(exc).__name__}:{exc}"
                LOGGER.warning("Falha de download %s: %s", doc_id, error)
        row["erro"] = error
        rows.append(row)
    for doc_id, previous in existing_by_doc.items():
        if doc_id not in selected_doc_ids:
            rows.append(previous)
    frame = pd.DataFrame(rows)
    write_csv(frame, existing_path)
    _register_hash_duplicates(context, frame)
    context.update_manifest(
        "download",
        documentos=len(frame),
        sucessos=int((frame["status_download"] == "sucesso").sum()),
        duplicatas=int((frame["status_download"] == "duplicata").sum()),
        falhas=int((frame["status_download"] == "falha").sum()),
    )
    return frame


def _extract_with_pymupdf(path: Path) -> list[str]:
    import pymupdf

    document = pymupdf.open(path)
    try:
        return [page.get_text("text") for page in document]
    finally:
        document.close()


def _extract_with_pdfplumber(path: Path) -> list[str]:
    import pdfplumber

    with pdfplumber.open(path) as document:
        return [page.extract_text() or "" for page in document.pages]


def extract_texts(context: RunContext, force: bool = False) -> pd.DataFrame:
    downloads = read_csv(context.paths.processed / "download_status.csv")
    config = context.pipeline_config["extracao"]
    existing_path = context.paths.processed / "extracao_status.csv"
    existing = read_csv(existing_path) if existing_path.exists() else pd.DataFrame()
    existing_by_doc = {
        row["doc_id"]: row for row in existing.to_dict("records")
    } if not existing.empty else {}
    rows: list[dict[str, Any]] = []
    threshold = int(config["minimo_caracteres_por_pagina"])
    for download in downloads.to_dict("records"):
        if download["status_download"] != "sucesso":
            continue
        doc_id = download["doc_id"]
        target = context.paths.text_raw / f"{doc_id}.txt"
        previous = existing_by_doc.get(doc_id)
        if previous and previous["status_extracao"] in {"sucesso", "parcial"} and target.exists() and not force:
            rows.append(previous)
            continue
        pdf_path = context.paths.root / download["arquivo_pdf"]
        method = "pymupdf"
        error = ""
        try:
            pages = _extract_with_pymupdf(pdf_path)
            if not any(page.strip() for page in pages):
                raise ValueError("pymupdf_sem_texto")
        except Exception as pymupdf_error:  # noqa: BLE001
            method = "pdfplumber"
            try:
                pages = _extract_with_pdfplumber(pdf_path)
            except Exception as pdfplumber_error:  # noqa: BLE001
                pages = []
                error = f"pymupdf:{pymupdf_error};pdfplumber:{pdfplumber_error}"
        chars_by_page = [len(page.strip()) for page in pages]
        pages_with_text = sum(chars >= threshold for chars in chars_by_page)
        total_chars = sum(chars_by_page)
        if not pages or total_chars == 0:
            status = "ocr_pendente"
        elif pages_with_text < len(pages):
            status = "parcial"
        else:
            status = "sucesso"
        target.write_text(f"\n{PAGE_BREAK}\n".join(pages), encoding="utf-8")
        rows.append(
            {
                "run_id": context.run_id,
                "as_of": context.as_of,
                "doc_id": doc_id,
                "metodo_extracao": method if total_chars else "falha",
                "paginas_total": len(pages),
                "paginas_com_texto": pages_with_text,
                "caracteres_extraidos": total_chars,
                "arquivo_txt_raw": str(target.relative_to(context.paths.root)),
                "arquivo_txt_clean": "",
                "status_extracao": status,
                "erro": error,
            }
        )
    frame = pd.DataFrame(rows)
    write_csv(frame, existing_path)
    context.update_manifest(
        "extract",
        documentos=len(frame),
        sucessos=int(frame["status_extracao"].isin(["sucesso", "parcial"]).sum()),
        ocr_pendente=int((frame["status_extracao"] == "ocr_pendente").sum()),
    )
    return frame


def _line_key(line: str) -> str:
    return re.sub(r"\d+", "#", normalize_text(line))


def _repeated_margin_lines(pages: list[str]) -> set[str]:
    if not pages:
        return set()
    counts: Counter[str] = Counter()
    for page in pages:
        lines = [line.strip() for line in page.splitlines() if line.strip()]
        keys = {_line_key(line) for line in (lines[:3] + lines[-3:]) if len(_line_key(line)) >= 3}
        counts.update(keys)
    minimum = max(3, math.ceil(len(pages) * 0.30))
    return {key for key, count in counts.items() if count >= minimum}


def clean_pages(pages: list[str]) -> list[str]:
    repeated = _repeated_margin_lines(pages)
    cleaned: list[str] = []
    for page in pages:
        lines = [line.rstrip() for line in page.splitlines()]
        nonempty_positions = [index for index, line in enumerate(lines) if line.strip()]
        margin_positions = set(nonempty_positions[:3] + nonempty_positions[-3:])
        kept = [
            line
            for index, line in enumerate(lines)
            if not (index in margin_positions and _line_key(line) in repeated)
        ]
        text = "\n".join(kept)
        text = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        cleaned.append(text.strip())
    return cleaned


def clean_texts(context: RunContext) -> pd.DataFrame:
    status_path = context.paths.processed / "extracao_status.csv"
    extraction = read_csv(status_path)
    rows: list[dict[str, Any]] = []
    for row in extraction.to_dict("records"):
        raw_path = context.paths.root / row["arquivo_txt_raw"]
        clean_path = context.paths.text_clean / f"{row['doc_id']}.txt"
        pages = raw_path.read_text(encoding="utf-8").split(PAGE_BREAK)
        cleaned = clean_pages(pages)
        clean_path.write_text(f"\n{PAGE_BREAK}\n".join(cleaned), encoding="utf-8")
        row["arquivo_txt_clean"] = str(clean_path.relative_to(context.paths.root))
        rows.append(row)
    frame = pd.DataFrame(rows)
    write_csv(frame, status_path)
    context.update_manifest("clean", documentos=len(frame))
    return frame


def build_corpus_index(context: RunContext) -> pd.DataFrame:
    catalog = read_csv(context.paths.processed / "catalogo_pdfs_aprovado.csv")
    downloads = read_csv(context.paths.processed / "download_status.csv")
    extractions = read_csv(context.paths.processed / "extracao_status.csv")
    frame = catalog.merge(downloads, on=["run_id", "as_of", "doc_id"], how="inner", suffixes=("", "_download"))
    frame = frame.merge(extractions, on=["run_id", "as_of", "doc_id"], how="inner", suffixes=("", "_extracao"))
    frame = frame[
        (frame["status_download"] == "sucesso")
        & frame["status_extracao"].isin(["sucesso", "parcial"])
    ].copy()
    corpus = pd.DataFrame(
        {
            "run_id": frame["run_id"],
            "as_of": frame["as_of"],
            "snapshot_sha256": frame["snapshot_sha256"],
            "doc_id": frame["doc_id"],
            "titulo": frame["titulo_inferido"],
            "ano": frame["ano_documento"],
            "ano_url": frame["ano_url"],
            "url": frame["url"],
            "secao_portal": frame["secao_portal"],
            "prioridade_analitica": frame["prioridade_analitica"],
            "tipo_documento": frame["tipo_documento"],
            "categoria": frame["categoria_inferida"],
            "idioma": frame["idioma_inferido"],
            "sha256": frame["sha256"],
            "arquivo_txt_clean": frame["arquivo_txt_clean"],
            "paginas_total": frame["paginas_total"],
            "incluido_em": utc_now(),
        }
    )
    write_csv(corpus, context.paths.processed / "corpus_documentos.csv")
    write_parquet(corpus, context.paths.processed / "corpus_documentos.parquet")
    context.update_manifest("corpus-index", documentos=len(corpus))
    return corpus


def _window_segments(text: str, window: int, overlap: int) -> list[tuple[int, int, str]]:
    if not text:
        return []
    if len(text) <= window:
        return [(0, len(text), text)]
    step = max(1, window - overlap)
    rows: list[tuple[int, int, str]] = []
    raw_start = 0
    while raw_start < len(text):
        raw_end = min(len(text), raw_start + window)
        start = raw_start
        end = raw_end
        if start > 0 and text[start - 1].isalnum() and text[start].isalnum():
            while start < end and not text[start].isspace():
                start += 1
            while start < end and text[start].isspace():
                start += 1
        if end < len(text) and text[end - 1].isalnum() and text[end].isalnum():
            while end > start and not text[end - 1].isspace():
                end -= 1
        if end <= start:
            start, end = raw_start, raw_end
        rows.append((start, end, text[start:end]))
        if raw_end >= len(text):
            break
        raw_start += step
    return rows


def segment_texts(context: RunContext) -> pd.DataFrame:
    corpus = read_csv(context.paths.processed / "corpus_documentos.csv")
    config = context.pipeline_config["segmentacao"]
    rows: list[dict[str, Any]] = []
    for document in corpus.to_dict("records"):
        clean_path = context.paths.root / document["arquivo_txt_clean"]
        pages = clean_path.read_text(encoding="utf-8").split(PAGE_BREAK)
        for page_number, page in enumerate(pages, start=1):
            text = page.strip()
            if not text:
                continue
            rows.append(_segment_row(document["doc_id"], page_number, "pagina", 0, len(text), text))
            cursor = 0
            for paragraph in re.split(r"\n\s*\n+", text):
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                start = text.find(paragraph, cursor)
                if start < 0:
                    start = cursor
                end = start + len(paragraph)
                cursor = end
                rows.append(_segment_row(document["doc_id"], page_number, "paragrafo", start, end, paragraph))
            for start, end, window_text in _window_segments(
                text,
                int(config["janela_caracteres"]),
                int(config["sobreposicao_caracteres"]),
            ):
                rows.append(_segment_row(document["doc_id"], page_number, "janela", start, end, window_text))
    frame = pd.DataFrame(rows)
    write_parquet(frame, context.paths.processed / "segmentos.parquet")
    write_csv(frame, context.paths.processed / "segmentos.csv")
    context.update_manifest("segment", segmentos=len(frame))
    return frame


def _segment_row(doc_id: str, page: int, kind: str, start: int, end: int, text: str) -> dict[str, Any]:
    return {
        "segmento_id": stable_id("seg", doc_id, page, kind, start, end),
        "doc_id": doc_id,
        "pagina": page,
        "tipo_segmento": kind,
        "char_inicio": start,
        "char_fim": end,
        "trecho": text,
    }


def build_corpus(context: RunContext, force: bool = False) -> dict[str, int]:
    downloads = download_pdfs(context, force=force)
    extractions = extract_texts(context, force=force)
    clean_texts(context)
    corpus = build_corpus_index(context)
    segments = segment_texts(context)
    summary = {
        "downloads": len(downloads),
        "extracoes": len(extractions),
        "documentos_corpus": len(corpus),
        "segmentos": len(segments),
    }
    context.update_manifest("corpus", **summary)
    return summary
