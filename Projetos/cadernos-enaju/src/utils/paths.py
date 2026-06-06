"""Resolução de caminhos do projeto, independente do diretório de execução."""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Raiz do projeto CADERNOS_ENAJU (pasta que contém README.md e src/)."""
    return Path(__file__).resolve().parents[2]


def docs_dir() -> Path:
    return project_root() / "docs"


def data_dir() -> Path:
    return project_root() / "data"


def outputs_dir() -> Path:
    return data_dir() / "outputs"


def references_dir() -> Path:
    return project_root() / "references"
