# Como contribuir — CADERNOS_ENAJU

Este repositório combina produção editorial, pesquisa aplicada e automação.
O fluxo abaixo vale para pessoas e para agentes operados no VS Code.

## Princípios

1. Toda contribuição preserva a **proveniência** (de onde veio cada evidência).
2. Insumos, processamento, produtos e publicação ficam **separados**.
3. Nada que envolva dados de pessoas entra no repositório sem **anonimização**
   e aderência à **LGPD**.
4. Decisões relevantes são registradas em
   [ficha-projeto.md](ficha-projeto.md) e no
   [charter](docs/projeto/charter.md).

## Fluxo de branches

| Branch | Uso |
| --- | --- |
| `main` | Versões estáveis e validadas institucionalmente |
| `develop` | Integração corrente |
| `feature/caderno-001` | Produção do Caderno ENAJU n. 1 |
| `feature/protocolo-piloto` | Protocolo de pesquisa |
| `feature/trilha-evidencias` | Trilha formativa derivada |
| `hotfix/*` | Correções urgentes |

Crie sempre uma branch a partir de `develop`. Abra Pull Request usando o
[template](.github/pull_request_template.md).

## Convenção de commits

Use prefixos curtos e descritivos:

- `docs:` documentos e cadernos
- `proto:` protocolos e instrumentos
- `trilha:` trilhas formativas
- `src:` código e automação
- `ref:` referências e fichamentos
- `chore:` infraestrutura, CI, configuração

Exemplo: `docs: estrutura inicial do Caderno 001`.

## Pipeline editorial (GitHub Projects)

```
backlog → em curadoria → em redação → em revisão → em validação institucional → publicado
```

Cada item nasce de uma [Issue](.github/ISSUE_TEMPLATE/):
novo caderno, protocolo de pesquisa ou trilha formativa.

## Padrões de documento

- Markdown com cabeçalhos hierárquicos e uma frase por linha sempre que possível.
- Tabelas para entregáveis, decisões e riscos.
- Citações e referências consolidadas em
  [references/bibliografia.bib](references/bibliografia.bib).
- Datas no formato `AAAA-MM-DD`.

## Antes de abrir o PR

```powershell
.\.venv\Scripts\python.exe src\automation\validar_estrutura.py
.\.venv\Scripts\python.exe -m pytest
```

A mesma validação roda no CI. PRs com estrutura inválida não devem ser
integrados.

## Agentes

Os agentes especializados (editorial, metodologia, formação, dados, curadoria,
revisão) seguem as instruções em [prompts/](prompts/). Toda saída de agente
passa por revisão humana antes de virar produto.
