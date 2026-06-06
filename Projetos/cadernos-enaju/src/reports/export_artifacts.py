"""Exporta artefatos prontos para publicação ou distribuição interna.

Esqueleto: a implementação converte os cadernos consolidados para o formato
escolhido (docx/pdf/html) e grava em data/outputs/.

Uso:
    python src/reports/export_artifacts.py --formato docx
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from utils.paths import outputs_dir  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Exporta artefatos do CADERNOS_ENAJU.")
    parser.add_argument(
        "--formato",
        choices=["docx", "pdf", "html"],
        default="docx",
        help="Formato de exportação.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    saida = outputs_dir()
    saida.mkdir(parents=True, exist_ok=True)
    print(f"[export_artifacts] Formato: {args.formato}")
    print(f"[export_artifacts] Pasta de saída pronta: {saida}")
    print("[export_artifacts] TODO: implementar exportação.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
