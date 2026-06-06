"""Gera versões consolidadas dos cadernos e notas técnicas.

Esqueleto: a implementação concatena/normaliza os documentos de docs/ e grava
em data/outputs/. Hoje apenas registra a intenção e cria a pasta de saída.

Uso:
    python src/reports/build_reports.py
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from utils.paths import outputs_dir  # noqa: E402


def main() -> int:
    saida = outputs_dir()
    saida.mkdir(parents=True, exist_ok=True)
    print(f"[build_reports] Pasta de saída pronta: {saida}")
    print("[build_reports] TODO: consolidar cadernos e notas técnicas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
