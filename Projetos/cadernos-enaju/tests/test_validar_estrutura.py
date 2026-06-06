"""Testes da validação de estrutura documental."""

from automation.validar_estrutura import _frontmatter_keys, validar
from utils.paths import project_root


def test_projeto_real_valido():
    """A estrutura atual do repositório deve passar na validação."""
    problemas = validar(project_root())
    assert problemas == [], "\n".join(problemas)


def test_frontmatter_keys_extrai_chaves_de_topo():
    texto = "---\nstatus: rascunho\nversao: '0.1'\ndata: '2026-06-06'\n  aninhada: x\n---\n# corpo\n"
    chaves = _frontmatter_keys(texto)
    assert {"status", "versao", "data"} <= chaves
    assert "aninhada" not in chaves  # chave aninhada não é de topo


def test_frontmatter_keys_sem_frontmatter():
    assert _frontmatter_keys("# só um título\n") == set()
