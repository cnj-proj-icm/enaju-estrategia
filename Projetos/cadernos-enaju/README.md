# CADERNOS_ENAJU

Linha estruturada de produção técnico-científica da **CODE — Coordenação de
Desenvolvimento, Pesquisa e Inovação** para fomentar pesquisas aplicadas e
apoiar a elaboração de trilhas formativas baseadas em evidências no Poder
Judiciário.

O piloto usa o artigo de validação brasileira do **REI-40** como referência
metodológica inicial para organizar uma agenda de pesquisa sobre estilos de
pensamento, tomada de decisão, inovação e formulação de políticas judiciárias.
A institucionalização da escala **não** é obrigatória: o projeto estrutura um
ambiente de pesquisa, documentação e experimentação em rede, com uso voluntário
e cientificamente orientado do instrumento.

## Estado atual

**Status:** estruturação inicial (Fase 1 — Implantação).

O repositório está em scaffold: estrutura de pastas, templates, governança
mínima, protocolos-base e prompts de agentes já criados. O conteúdo substantivo
do Caderno ENAJU n. 1 e os dados de pesquisa ainda serão produzidos.

## Produto-piloto

**Caderno ENAJU n. 1 — Estilos de pensamento, inovação e políticas judiciárias:
bases para pesquisa aplicada e trilhas formativas baseadas em evidências.**

Rascunho estruturado em
[docs/cadernos/caderno-001-estilos-pensamento.md](docs/cadernos/caderno-001-estilos-pensamento.md).

## Mapa do repositório

| Local | Conteúdo |
| --- | --- |
| [cadernos_enaju_projeto.md](cadernos_enaju_projeto.md) | Documento-mãe: planejamento integral do projeto |
| [ficha-projeto.md](ficha-projeto.md) | Registro institucional, entregáveis, decisões e riscos |
| [docs/projeto/](docs/projeto/) | Charter, governança, cronograma e parceiros |
| [docs/cadernos/](docs/cadernos/) | Cadernos temáticos e seus templates |
| [docs/protocolos/](docs/protocolos/) | Protocolo-piloto REI-40, modelo de TCLE e questionários |
| [docs/trilhas/](docs/trilhas/) | Template de trilha baseada em evidências e casos |
| [docs/notas-tecnicas/](docs/notas-tecnicas/) | Notas executivas para ENAJU e parceiros |
| [prompts/](prompts/) | Instruções dos agentes especializados no VS Code |
| [references/](references/) | Artigos, fichamentos e `bibliografia.bib` |
| [src/](src/) | Automação, análise e geração de produtos (Python) |
| [data/](data/) | Insumos (`raw`), processados e saídas — não versionados |

## Estrutura prevista

```text
cadernos-enaju/
├── .github/            # workflows, issue templates, PR template
├── .vscode/            # settings, tasks, extensions, launch
├── docs/
│   ├── projeto/        # charter, governanca, cronograma, parceiros
│   ├── cadernos/       # produtos editoriais + templates
│   ├── protocolos/     # protocolo-piloto, TCLE, questionarios
│   ├── trilhas/        # template de trilha + casos
│   └── notas-tecnicas/
├── data/               # raw, processed, dictionaries, outputs (git-ignored)
├── src/                # analysis, automation, forms, reports, utils
├── prompts/            # agentes especializados
├── references/         # artigos, fichamentos, bibliografia.bib
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

## Princípios de execução

1. **Modularidade** — separar insumos, processamento, produtos e publicação.
2. **Reprodutibilidade** — protocolos replicáveis em labs, escolas e equipes.
3. **Rastreabilidade** — versionar decisões, fontes e proveniência das evidências.
4. **Colaboração humano-agente** — agentes apoiam, pessoas decidem.
5. **Conformidade** — anonimização, LGPD e uso voluntário do instrumento.

## Fluxo de trabalho

- Branches: `main` (estável), `develop` (integração),
  `feature/caderno-001`, `feature/protocolo-piloto`,
  `feature/trilha-evidencias`, `hotfix/*`.
- Pipeline (GitHub Projects): backlog → em curadoria → em redação → em revisão →
  em validação institucional → publicado.
- Abertura de trabalho por [Issues](.github/ISSUE_TEMPLATE/) e revisão por
  [Pull Request](.github/pull_request_template.md).

## Execução local

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.in
.\.venv\Scripts\python.exe src\automation\validar_estrutura.py
```

A validação documental também roda no CI a cada push/PR
(ver [.github/workflows/validate_docs.yml](.github/workflows/validate_docs.yml)).

## Próximos passos

1. Aprovar o [charter](docs/projeto/charter.md) no âmbito da CODE.
2. Fichar o artigo de validação do REI-40 em
   [references/fichamentos/](references/fichamentos/).
3. Fechar o [protocolo-piloto](docs/protocolos/protocolo-rei40-piloto.md) e o
   modelo de TCLE.
4. Redigir o Caderno ENAJU n. 1 e a nota executiva à ENAJU.
5. Derivar o [template de trilha](docs/trilhas/template-trilha-evidencias.md)
   para um caso real.

---

Projeto da CODE no âmbito do ecossistema **ENAJU**. Ver
[CONTRIBUTING.md](CONTRIBUTING.md) para o fluxo de colaboração.
