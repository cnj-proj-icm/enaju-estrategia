"""Valida a estrutura de pastas e os metadados dos documentos do CADERNOS_ENAJU.

Uso:
    python src/automation/validar_estrutura.py

Sai com código 0 se tudo estiver válido; 1 se houver problemas.
Não depende de bibliotecas externas para rodar antes da instalação.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Permite importar utils.* quando executado como script.
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from utils.paths import project_root  # noqa: E402

# Pastas que precisam existir.
PASTAS_OBRIGATORIAS = [
    "docs/projeto",
    "docs/cadernos",
    "docs/cadernos/templates",
    "docs/protocolos",
    "docs/trilhas",
    "docs/notas-tecnicas",
    "data/raw",
    "data/processed",
    "data/dictionaries",
    "data/outputs",
    "src/automation",
    "src/analysis",
    "src/reports",
    "src/utils",
    "prompts",
    "references/fichamentos",
]

# Arquivos que precisam existir.
ARQUIVOS_OBRIGATORIOS = [
    "README.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "ficha-projeto.md",
    "cadernos_enaju_projeto.md",
    ".gitignore",
    "requirements.in",
    "docs/projeto/charter.md",
    "docs/projeto/governanca.md",
    "docs/projeto/cronograma.md",
    "docs/cadernos/templates/template-caderno.md",
    "docs/protocolos/protocolo-rei40-piloto.md",
    "docs/protocolos/tcle-modelo.md",
    "docs/trilhas/template-trilha-evidencias.md",
    "references/bibliografia.bib",
    "prompts/README.md",
]

# Documentos cujo frontmatter deve conter estas chaves.
CHAVES_FRONTMATTER = ("status", "versao", "data")
DOCS_COM_FRONTMATTER = [
    "docs/cadernos/caderno-001-estilos-pensamento.md",
    "docs/cadernos/templates/template-caderno.md",
    "docs/protocolos/protocolo-rei40-piloto.md",
    "docs/protocolos/tcle-modelo.md",
    "docs/trilhas/template-trilha-evidencias.md",
    "docs/notas-tecnicas/nota-tecnica-001-apresentacao-enaju.md",
]


def _frontmatter_keys(texto: str) -> set[str]:
    """Extrai as chaves de topo de um frontmatter YAML delimitado por '---'."""
    linhas = texto.splitlines()
    if not linhas or linhas[0].strip() != "---":
        return set()
    chaves: set[str] = set()
    for linha in linhas[1:]:
        if linha.strip() == "---":
            break
        if linha and not linha[0].isspace() and ":" in linha:
            chaves.add(linha.split(":", 1)[0].strip())
    return chaves


def validar(raiz: Path) -> list[str]:
    problemas: list[str] = []

    for pasta in PASTAS_OBRIGATORIAS:
        if not (raiz / pasta).is_dir():
            problemas.append(f"Pasta ausente: {pasta}")

    for arquivo in ARQUIVOS_OBRIGATORIOS:
        if not (raiz / arquivo).is_file():
            problemas.append(f"Arquivo ausente: {arquivo}")

    for doc in DOCS_COM_FRONTMATTER:
        caminho = raiz / doc
        if not caminho.is_file():
            problemas.append(f"Documento ausente: {doc}")
            continue
        chaves = _frontmatter_keys(caminho.read_text(encoding="utf-8"))
        faltando = [c for c in CHAVES_FRONTMATTER if c not in chaves]
        if faltando:
            problemas.append(
                f"Frontmatter incompleto em {doc}: faltam {', '.join(faltando)}"
            )

    return problemas


def main() -> int:
    raiz = project_root()
    problemas = validar(raiz)
    if problemas:
        print(f"[validar_estrutura] {len(problemas)} problema(s) encontrado(s):")
        for p in problemas:
            print(f"  - {p}")
        return 1
    print("[validar_estrutura] Estrutura válida.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
