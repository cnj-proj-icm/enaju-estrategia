from __future__ import annotations

import json
import logging

import requests

from .common import RunContext, sha256_bytes, utc_now

LOGGER = logging.getLogger(__name__)


def create_snapshot(context: RunContext, force: bool = False) -> dict[str, str | int]:
    if context.snapshot_html.exists() and context.snapshot_metadata.exists() and not force:
        LOGGER.info("Snapshot existente reutilizado: %s", context.snapshot_html)
        metadata = json.loads(context.snapshot_metadata.read_text(encoding="utf-8"))
        context.update_manifest("snapshot", **metadata)
        return metadata

    config = context.pipeline_config
    source_url = config["fonte"]["url"]
    timeout = config["download"]["timeout_segundos"]
    LOGGER.info("Baixando snapshot editorial: %s", source_url)
    response = requests.get(
        source_url,
        timeout=timeout,
        headers={"User-Agent": "ENAJU-lacunas-capacitacao-cnj/0.1"},
    )
    response.raise_for_status()
    content = response.content
    snapshot_hash = sha256_bytes(content)
    context.snapshot_html.write_bytes(content)
    metadata: dict[str, str | int] = {
        "run_id": context.run_id,
        "as_of": context.as_of,
        "source_url": source_url,
        "fetched_at": utc_now(),
        "snapshot_sha256": snapshot_hash,
        "http_status": response.status_code,
        "content_type": response.headers.get("content-type", ""),
        "bytes": len(content),
        "snapshot_file": str(context.snapshot_html.relative_to(context.paths.root)),
    }
    context.snapshot_metadata.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    context.update_manifest("snapshot", **metadata)
    LOGGER.info("Snapshot salvo com SHA-256 %s", snapshot_hash)
    return metadata
