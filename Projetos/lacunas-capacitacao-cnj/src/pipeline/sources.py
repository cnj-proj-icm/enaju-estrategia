from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .common import read_yaml

REQUIRED_FIELDS = ("name", "url", "section", "priority", "type")
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def validate_source_registry(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(entries, list) or not entries:
        raise ValueError("Fonte de dados invalida: esperado uma lista nao vazia de entradas.")

    normalized: list[dict[str, Any]] = []
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"Entrada de fonte #{index} deve ser um objeto YAML.")
        missing = [field for field in REQUIRED_FIELDS if not str(entry.get(field, "")).strip()]
        if missing:
            raise ValueError(f"Entrada de fonte #{index} sem campos obrigatorios: {', '.join(missing)}")

        normalized_entry = dict(entry)
        normalized_entry.setdefault("enabled", True)
        normalized_entry.setdefault("description", "")
        normalized_entry["priority"] = str(normalized_entry["priority"]).strip().lower()
        if normalized_entry["priority"] not in PRIORITY_ORDER:
            raise ValueError(f"Prioridade invalida na fonte '{entry['name']}': {entry['priority']}")
        normalized.append(normalized_entry)

    return sorted(normalized, key=lambda item: (PRIORITY_ORDER[item["priority"]], item["name"]))


def load_source_registry(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de fontes nao encontrado: {path}")

    payload = read_yaml(path)
    if isinstance(payload, dict) and "sources" in payload:
        entries = payload["sources"]
    else:
        entries = payload

    return validate_source_registry(entries)


def enabled_sources(path: Path) -> list[dict[str, Any]]:
    return [entry for entry in load_source_registry(path) if entry.get("enabled", True)]
