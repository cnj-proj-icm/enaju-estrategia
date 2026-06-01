from __future__ import annotations

import csv
import hashlib
import json
import logging
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import pandas as pd
import yaml

CSV_ENCODING = "utf-8-sig"
PAGE_BREAK = "===PAGE_BREAK==="
TARGET_SECTIONS = {
    "producao interna": "Producao Interna",
    "parcerias institucionais": "Parcerias Institucionais",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.casefold()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def slugify(value: Any) -> str:
    text = normalize_text(value)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def stable_id(prefix: str, *parts: Any, size: int = 16) -> str:
    payload = "\x1f".join(str(part or "") for part in parts)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:size]
    return f"{prefix}_{digest}"


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    query = urlencode(sorted(parse_qsl(parsed.query, keep_blank_values=True)))
    return urlunsplit(
        (
            parsed.scheme.casefold(),
            parsed.netloc.casefold(),
            parsed.path,
            query,
            "",
        )
    )


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def json_loads(value: Any, default: Any) -> Any:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return default
    if isinstance(value, (list, dict)):
        return value
    text = str(value).strip()
    if not text:
        return default
    return json.loads(text)


def write_csv(rows: Iterable[dict[str, Any]] | pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(list(rows))
    frame.to_csv(path, index=False, encoding=CSV_ENCODING, quoting=csv.QUOTE_MINIMAL)


def write_parquet(rows: Iterable[dict[str, Any]] | pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(list(rows))
    frame.to_parquet(path, index=False)


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding=CSV_ENCODING, keep_default_na=False)


def read_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@dataclass(frozen=True)
class ProjectPaths:
    root: Path

    @classmethod
    def discover(cls) -> "ProjectPaths":
        return cls(Path(__file__).resolve().parents[2])

    @property
    def config(self) -> Path:
        return self.root / "config"

    @property
    def data(self) -> Path:
        return self.root / "data"

    @property
    def raw_html(self) -> Path:
        return self.data / "raw_html"

    @property
    def raw_pdf(self) -> Path:
        return self.data / "raw_pdf"

    @property
    def text_raw(self) -> Path:
        return self.data / "text" / "raw"

    @property
    def text_clean(self) -> Path:
        return self.data / "text" / "clean"

    @property
    def processed(self) -> Path:
        return self.data / "processed"

    @property
    def logs(self) -> Path:
        return self.data / "logs"

    @property
    def outputs(self) -> Path:
        return self.root / "outputs"

    def ensure(self) -> None:
        for path in (
            self.raw_html,
            self.raw_pdf,
            self.text_raw,
            self.text_clean,
            self.processed,
            self.logs,
            self.outputs,
        ):
            path.mkdir(parents=True, exist_ok=True)


@dataclass
class RunContext:
    paths: ProjectPaths
    run_id: str
    as_of: str

    @classmethod
    def create(cls, run_id: str, as_of: str) -> "RunContext":
        paths = ProjectPaths.discover()
        paths.ensure()
        return cls(paths=paths, run_id=run_id, as_of=as_of)

    @property
    def pipeline_config(self) -> dict[str, Any]:
        return read_yaml(self.paths.config / "pipeline.yml")

    @property
    def criteria_config(self) -> dict[str, Any]:
        return read_yaml(self.paths.config / "criterios_analiticos.yml")

    @property
    def snapshot_html(self) -> Path:
        return self.paths.raw_html / f"{self.run_id}.html"

    @property
    def snapshot_metadata(self) -> Path:
        return self.paths.raw_html / f"{self.run_id}.json"

    @property
    def manifest_path(self) -> Path:
        return self.paths.processed / "manifest_run.json"

    def load_manifest(self) -> dict[str, Any]:
        if self.manifest_path.exists():
            return json.loads(self.manifest_path.read_text(encoding="utf-8"))
        return {
            "run_id": self.run_id,
            "as_of": self.as_of,
            "created_at": utc_now(),
            "criteria_version": self.criteria_config["versao"],
            "steps": {},
        }

    def update_manifest(self, step: str, **details: Any) -> None:
        manifest = self.load_manifest()
        manifest["run_id"] = self.run_id
        manifest["as_of"] = self.as_of
        manifest["criteria_version"] = self.criteria_config["versao"]
        manifest["updated_at"] = utc_now()
        manifest.setdefault("steps", {})[step] = {
            "completed_at": utc_now(),
            **details,
        }
        self.manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )


def configure_logging(paths: ProjectPaths, run_id: str, verbose: bool = False) -> None:
    paths.ensure()
    handlers: list[logging.Handler] = [
        logging.FileHandler(paths.logs / f"{run_id}.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
        force=True,
    )
